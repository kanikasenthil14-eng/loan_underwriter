"""REST API routes for programmatic access."""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from bson import ObjectId
from app import mongo
from app.utils.pipeline import run_pipeline
from app.models.application_model import application_schema
from datetime import datetime

api_bp = Blueprint('api', __name__)

def _serialize(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc

@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Insurance Underwriting API'})

@api_bp.route('/applications', methods=['GET'])
@login_required
def get_applications():
    if current_user.is_admin():
        apps = list(mongo.db.applications.find().sort('submitted_at', -1).limit(50))
    else:
        apps = list(mongo.db.applications.find({'user_id': current_user.id}).sort('submitted_at', -1))
    return jsonify([_serialize(a) for a in apps])

@api_bp.route('/applications/<app_id>', methods=['GET'])
@login_required
def get_application(app_id):
    try:
        query = {'_id': ObjectId(app_id)}
        if not current_user.is_admin():
            query['user_id'] = current_user.id
        app = mongo.db.applications.find_one(query)
        if not app:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(_serialize(app))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    return jsonify({
        'total': mongo.db.applications.count_documents({}),
        'approved': mongo.db.applications.count_documents({'decision.final_decision': 'Approved'}),
        'rejected': mongo.db.applications.count_documents({'decision.final_decision': 'Rejected'}),
        'manual_review': mongo.db.applications.count_documents({'decision.final_decision': 'Manual Review'}),
        'fraud_flagged': mongo.db.applications.count_documents({'fraud_detection.is_suspicious': True}),
        'total_users': mongo.db.users.count_documents({'role': 'customer'})
    })

@api_bp.route('/applications/<app_id>/reprocess', methods=['POST'])
@login_required
def reprocess(app_id):
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    try:
        app = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
        if not app:
            return jsonify({'error': 'Not found'}), 404
        enriched = run_pipeline(app)
        enriched['status'] = 'processed'
        enriched['updated_at'] = datetime.utcnow()
        update_data = {k: v for k, v in enriched.items() if k != '_id'}
        mongo.db.applications.update_one({'_id': ObjectId(app_id)}, {'$set': update_data})
        return jsonify({'message': 'Reprocessed successfully', 'decision': enriched.get('decision', {})})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
