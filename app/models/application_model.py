from datetime import datetime

def application_schema(user_id, form_data, doc_paths):
    return {
        'user_id': str(user_id),
        'status': 'pending',
        'submitted_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),

        # Personal Info
        'full_name': form_data.get('full_name', ''),
        'age': int(form_data.get('age', 0)),
        'gender': form_data.get('gender', ''),
        'mobile': form_data.get('mobile', ''),
        'email': form_data.get('email', ''),
        'address': form_data.get('address', ''),

        # Loan Info
        'loan_type': form_data.get('loan_purpose', form_data.get('loan_type', 'personal')),
        'loan_amount': float(form_data.get('loan_amount', 0)),
        'loan_tenure': int(form_data.get('loan_tenure', 12)),
        'loan_purpose': form_data.get('loan_purpose', form_data.get('loan_type', 'personal')),

        # Financial Info
        'occupation': form_data.get('occupation', ''),
        'employment_status': form_data.get('employment_status', ''),
        'annual_income': float(form_data.get('annual_income', 0)),
        'credit_score': int(form_data.get('credit_score', 700)),
        'existing_loans': int(form_data.get('existing_loans', 0)),

        # Documents
        'documents': doc_paths,

        # AI Agent Results
        'doc_verification': {},
        'financial_risk': {},
        'fraud_detection': {},
        'risk_score': {},
        'ml_prediction': {},
        'decision': {},
        'loan_terms': {},
        'report': {}
    }
