from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from bson import ObjectId
from app import mongo
from app.utils.helpers import applications_to_csv
from datetime import datetime, timedelta
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total = mongo.db.applications.count_documents({})
    approved = mongo.db.applications.count_documents({'decision.final_decision': 'Approved'})
    rejected = mongo.db.applications.count_documents({'decision.final_decision': 'Rejected'})
    manual = mongo.db.applications.count_documents({'decision.final_decision': 'Manual Review'})
    pending = mongo.db.applications.count_documents({'status': 'pending'})
    fraud_flagged = mongo.db.applications.count_documents({'fraud_detection.is_suspicious': True})
    total_users = mongo.db.users.count_documents({'role': 'customer'})

    # Recent applications
    recent = list(mongo.db.applications.find().sort('submitted_at', -1).limit(10))

    # Monthly trend (last 6 months)
    monthly_data = _get_monthly_trend()

    # Risk distribution
    risk_dist = _get_risk_distribution()

    # Premium revenue
    premium_data = _get_premium_stats()

    stats = {
        'total': total, 'approved': approved, 'rejected': rejected,
        'manual': manual, 'pending': pending, 'fraud_flagged': fraud_flagged,
        'total_users': total_users,
        'approval_rate': round((approved / total * 100) if total > 0 else 0, 1),
        'rejection_rate': round((rejected / total * 100) if total > 0 else 0, 1)
    }

    return render_template('admin/dashboard.html',
        stats=stats, recent_applications=recent,
        monthly_data=monthly_data, risk_dist=risk_dist, premium_data=premium_data)

@admin_bp.route('/applications')
@login_required
@admin_required
def applications():
    page = int(request.args.get('page', 1))
    per_page = 20
    search = request.args.get('search', '')
    decision_filter = request.args.get('decision', '')

    query = {}
    if search:
        query['$or'] = [
            {'full_name': {'$regex': search, '$options': 'i'}},
            {'email': {'$regex': search, '$options': 'i'}}
        ]
    if decision_filter:
        query['decision.final_decision'] = decision_filter

    total = mongo.db.applications.count_documents(query)
    apps = list(mongo.db.applications.find(query)
                .sort('submitted_at', -1)
                .skip((page - 1) * per_page)
                .limit(per_page))

    return render_template('admin/applications.html',
        applications=apps, page=page, per_page=per_page,
        total=total, search=search, decision_filter=decision_filter,
        total_pages=(total + per_page - 1) // per_page)

@admin_bp.route('/application/<app_id>')
@login_required
@admin_required
def view_application(app_id):
    try:
        app = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
        if not app:
            flash('Application not found.', 'danger')
            return redirect(url_for('admin.applications'))
        return render_template('admin/application_detail.html', application=app)
    except Exception:
        flash('Invalid application ID.', 'danger')
        return redirect(url_for('admin.applications'))

@admin_bp.route('/application/<app_id>/override', methods=['POST'])
@login_required
@admin_required
def override_decision(app_id):
    try:
        new_decision = request.form.get('decision')
        reason = request.form.get('reason', 'Admin override')
        if new_decision not in ['Approved', 'Manual Review', 'Rejected']:
            flash('Invalid decision.', 'danger')
            return redirect(url_for('admin.view_application', app_id=app_id))

        mongo.db.applications.update_one(
            {'_id': ObjectId(app_id)},
            {'$set': {
                'decision.final_decision': new_decision,
                'decision.reason': f'Admin Override: {reason}',
                'decision.override_applied': True,
                'decision.overridden_by': current_user.email,
                'decision.overridden_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        flash(f'Decision overridden to {new_decision}.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('admin.view_application', app_id=app_id))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = list(mongo.db.users.find({'role': 'customer'}).sort('created_at', -1))
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/export')
@login_required
@admin_required
def export_csv():
    apps = list(mongo.db.applications.find())
    csv_data = applications_to_csv(apps)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=underwriting_export.csv'}
    )

def _get_monthly_trend():
    months = []
    for i in range(5, -1, -1):
        d = datetime.utcnow() - timedelta(days=30 * i)
        label = d.strftime('%b %Y')
        start = datetime(d.year, d.month, 1)
        end = datetime(d.year, d.month + 1, 1) if d.month < 12 else datetime(d.year + 1, 1, 1)
        count = mongo.db.applications.count_documents({'submitted_at': {'$gte': start, '$lt': end}})
        months.append({'label': label, 'count': count})
    return months

def _get_risk_distribution():
    bands = ['A - Very Low Risk', 'B - Low Risk', 'C - Moderate Risk', 'D - High Risk', 'E - Very High Risk']
    return [{'band': b, 'count': mongo.db.applications.count_documents({'risk_score.risk_band': b})} for b in bands]

def _get_premium_stats():
    pipeline = [
        {'$match': {'decision.final_decision': 'Approved'}},
        {'$group': {'_id': None, 'total': {'$sum': '$premium.annual_premium'}, 'count': {'$sum': 1}}}
    ]
    result = list(mongo.db.applications.aggregate(pipeline))
    if result:
        return {'total_revenue': round(result[0]['total'], 2), 'count': result[0]['count']}
    return {'total_revenue': 0, 'count': 0}
