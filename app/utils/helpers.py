"""Utility helpers for file handling and data export."""
import os
import csv
import io
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, subfolder=''):
    """Save uploaded file and return its path."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        return filepath
    return None

def applications_to_csv(applications):
    """Convert applications list to CSV string for export."""
    output = io.StringIO()
    if not applications:
        return output.getvalue()

    fieldnames = [
        'application_id', 'full_name', 'age', 'gender', 'email', 'mobile',
        'occupation', 'employment_status', 'annual_income', 'credit_score',
        'existing_loans', 'previous_claims', 'insurance_type',
        'final_decision', 'composite_risk_score', 'fraud_score',
        'annual_premium', 'coverage_amount', 'submitted_at', 'status'
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()

    for app in applications:
        row = {
            'application_id': str(app.get('_id', '')),
            'full_name': app.get('full_name', ''),
            'age': app.get('age', ''),
            'gender': app.get('gender', ''),
            'email': app.get('email', ''),
            'mobile': app.get('mobile', ''),
            'occupation': app.get('occupation', ''),
            'employment_status': app.get('employment_status', ''),
            'annual_income': app.get('annual_income', ''),
            'credit_score': app.get('credit_score', ''),
            'existing_loans': app.get('existing_loans', ''),
            'previous_claims': app.get('previous_claims', ''),
            'insurance_type': app.get('insurance_type', ''),
            'final_decision': app.get('decision', {}).get('final_decision', ''),
            'composite_risk_score': app.get('risk_score', {}).get('composite_score', ''),
            'fraud_score': app.get('fraud_detection', {}).get('fraud_score', ''),
            'annual_premium': app.get('premium', {}).get('annual_premium', ''),
            'coverage_amount': app.get('premium', {}).get('coverage_amount', ''),
            'submitted_at': str(app.get('submitted_at', '')),
            'status': app.get('status', '')
        }
        writer.writerow(row)

    return output.getvalue()
