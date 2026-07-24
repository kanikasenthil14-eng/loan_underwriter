"""
Report Generation Agent
Generates a structured underwriting report from all agent outputs.
"""
from datetime import datetime

def run(application_data):
    """Generate comprehensive underwriting report."""
    decision = application_data.get('decision', {})
    risk_score = application_data.get('risk_score', {})
    financial = application_data.get('financial_risk', {})
    fraud = application_data.get('fraud_detection', {})
    doc_ver = application_data.get('doc_verification', {})
    premium = application_data.get('premium', {})
    ml_pred = application_data.get('ml_prediction', {})

    report = {
        'report_id': f"RPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        'generated_at': datetime.utcnow().isoformat(),
        'applicant_name': application_data.get('full_name', 'N/A'),
        'application_summary': {
            'loan_purpose': application_data.get('loan_purpose', 'N/A').title(),
            'loan_amount': application_data.get('loan_amount', 0),
            'submission_date': str(application_data.get('submitted_at', datetime.utcnow())),
            'final_decision': decision.get('final_decision', 'Pending'),
            'decision_confidence': f"{decision.get('confidence', 0):.0%}",
            'decision_reason': decision.get('reason', 'N/A')
        },
        'risk_summary': {
            'composite_score': risk_score.get('composite_score', 0),
            'risk_band': risk_score.get('risk_band', 'N/A'),
            'financial_risk_level': financial.get('risk_level', 'N/A'),
            'fraud_risk_level': fraud.get('risk_level', 'N/A'),
            'document_status': doc_ver.get('status', 'N/A')
        },
        'ml_analysis': {
            'model': 'Random Forest Classifier',
            'prediction': ml_pred.get('decision', 'N/A'),
            'confidence': f"{ml_pred.get('confidence', 0):.0%}",
            'features_analyzed': ml_pred.get('features_count', 8)
        },
        'loan_terms': {
            'loan_amount': premium.get('loan_amount', 0),
            'emi': premium.get('emi', 0),
            'interest_rate': premium.get('interest_rate', 0),
            'total_payable': premium.get('total_payable', 0),
            'tenure_months': premium.get('tenure_months', 0)
        },
        'conditions': decision.get('conditions', []),
        'fraud_flags': fraud.get('flags', []),
        'document_issues': doc_ver.get('issues', []),
        'recommendations': [
            risk_score.get('recommendation', ''),
            financial.get('recommendation', ''),
            fraud.get('recommendation', '')
        ],
        'agent': 'Report Generation Agent'
    }

    return report
