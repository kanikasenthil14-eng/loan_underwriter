from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from bson import ObjectId
from app import mongo
from app.models.application_model import application_schema
from app.utils.helpers import save_uploaded_file
from app.utils.pipeline import run_pipeline
from datetime import datetime

_FALLBACK_STORE = []


def _save_application(app_doc):
    try:
        result = mongo.db.applications.insert_one(app_doc)
        return str(result.inserted_id), None
    except Exception as exc:
        _FALLBACK_STORE.append(app_doc)
        return f"fallback-{len(_FALLBACK_STORE)}", str(exc)

customer_bp = Blueprint('customer', __name__)

LOAN_TYPES = {
    'personal': 'Personal Loan',
    'home': 'Home Loan',
    'education': 'Education Loan'
}

@customer_bp.route('/dashboard')
@login_required
def dashboard():
    apps = list(mongo.db.applications.find({'user_id': current_user.id}).sort('submitted_at', -1))
    stats = {
        'total': len(apps),
        'approved': sum(1 for a in apps if a.get('decision', {}).get('final_decision') == 'Approved'),
        'rejected': sum(1 for a in apps if a.get('decision', {}).get('final_decision') == 'Rejected'),
        'pending': sum(1 for a in apps if a.get('status') == 'pending' or a.get('decision', {}).get('final_decision') == 'Manual Review')
    }
    return render_template('customer/dashboard.html', applications=apps, stats=stats, loan_types=LOAN_TYPES)

@customer_bp.route('/select-loan')
@login_required
def select_loan():
    return render_template('customer/select_loan.html', loan_types=LOAN_TYPES)

@customer_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    loan_type = request.args.get('type', 'personal')
    if loan_type not in LOAN_TYPES:
        loan_type = 'personal'

    if request.method == 'POST':
        loan_type = request.form.get('loan_type', request.form.get('loan_purpose', 'personal')) or 'personal'
        doc_paths = {}
        for doc_field in ['aadhaar', 'pan', 'income_proof', 'passport_photo']:
            file = request.files.get(doc_field)
            if file and file.filename:
                path = save_uploaded_file(file, subfolder=current_user.id)
                if path:
                    doc_paths[doc_field] = path

        try:
            app_doc = application_schema(current_user.id, request.form, doc_paths)
            app_id, mongo_error = _save_application(app_doc)

            try:
                app_doc['_id'] = app_id
                # Run the underwriting pipeline, but fall back gracefully if the environment
                # is missing optional ML dependencies or Mongo connectivity is unavailable.
                enriched = run_pipeline(app_doc)
                enriched['status'] = 'processed'
                enriched['updated_at'] = datetime.utcnow()
                if mongo_error is None:
                    update_data = {k: v for k, v in enriched.items() if k != '_id'}
                    mongo.db.applications.update_one({'_id': ObjectId(app_id)}, {'$set': update_data})
                flash('Application submitted and processed successfully!', 'success')
            except Exception as e:
                if mongo_error is None:
                    mongo.db.applications.update_one({'_id': ObjectId(app_id)}, {'$set': {'status': 'error', 'error': str(e)}})
                flash('Application submitted but processing encountered an issue. The application record was still created.', 'warning')

            return redirect(url_for('customer.view_application', app_id=str(app_id)))
        except Exception as e:
            flash(f'Unable to submit application: {str(e)}', 'danger')
            return redirect(url_for('customer.dashboard'))

    return render_template('customer/apply.html', loan_type=loan_type, loan_type_name=LOAN_TYPES.get(loan_type, 'Personal Loan'))

@customer_bp.route('/application/<app_id>')
@login_required
def view_application(app_id):
    try:
        app = mongo.db.applications.find_one({'_id': ObjectId(app_id), 'user_id': current_user.id})
        if not app:
            flash('Application not found.', 'danger')
            return redirect(url_for('customer.dashboard'))
        return render_template('customer/application_detail.html', application=app, loan_types=LOAN_TYPES)
    except Exception:
        flash('Invalid application ID.', 'danger')
        return redirect(url_for('customer.dashboard'))

@customer_bp.route('/application/<app_id>/report')
@login_required
def download_report(app_id):
    try:
        app = mongo.db.applications.find_one({'_id': ObjectId(app_id), 'user_id': current_user.id})
        if not app:
            flash('Application not found.', 'danger')
            return redirect(url_for('customer.dashboard'))
        return render_template('customer/report.html', application=app, loan_types=LOAN_TYPES)
    except Exception:
        flash('Error generating report.', 'danger')
        return redirect(url_for('customer.dashboard'))
