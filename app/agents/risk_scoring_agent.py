"""
Risk Scoring Agent
Combines all risk factors into a single composite risk score.
"""

WEIGHTS = {
    'financial_risk': 0.35,
    'fraud_risk': 0.30,
    'doc_verification': 0.20,
    'age_risk': 0.15
}

def run(application_data):
    """Compute composite risk score from all agent outputs."""
    financial = application_data.get('financial_risk', {})
    fraud = application_data.get('fraud_detection', {})
    doc_ver = application_data.get('doc_verification', {})
    age = int(application_data.get('age', 30))

    # Normalize each component to 0-100
    financial_score = float(financial.get('total_risk_score', 50))
    fraud_score = float(fraud.get('fraud_score', 0))
    doc_score = 100 - float(doc_ver.get('score', 100))  # Invert: lower doc score = higher risk
    age_score = _age_risk_score(age)

    composite = (
        financial_score * WEIGHTS['financial_risk'] +
        fraud_score * WEIGHTS['fraud_risk'] +
        doc_score * WEIGHTS['doc_verification'] +
        age_score * WEIGHTS['age_risk']
    )
    composite = round(min(composite, 100), 2)

    breakdown = {
        'financial_component': round(financial_score * WEIGHTS['financial_risk'], 2),
        'fraud_component': round(fraud_score * WEIGHTS['fraud_risk'], 2),
        'document_component': round(doc_score * WEIGHTS['doc_verification'], 2),
        'age_component': round(age_score * WEIGHTS['age_risk'], 2)
    }

    risk_band = _risk_band(composite)

    return {
        'composite_score': composite,
        'risk_band': risk_band,
        'breakdown': breakdown,
        'weights_used': WEIGHTS,
        'recommendation': _risk_recommendation(risk_band),
        'agent': 'Risk Scoring Agent'
    }

def _age_risk_score(age):
    """Age-based risk: very young and very old are higher risk."""
    if 25 <= age <= 45: return 10
    if 18 <= age < 25: return 30
    if 46 <= age <= 55: return 25
    if 56 <= age <= 65: return 45
    return 70

def _risk_band(score):
    if score <= 25: return 'A - Very Low Risk'
    if score <= 40: return 'B - Low Risk'
    if score <= 55: return 'C - Moderate Risk'
    if score <= 70: return 'D - High Risk'
    return 'E - Very High Risk'

def _risk_recommendation(band):
    mapping = {
        'A - Very Low Risk': 'Excellent profile. Fast-track approval recommended.',
        'B - Low Risk': 'Good profile. Standard approval process.',
        'C - Moderate Risk': 'Average risk. Standard review with possible conditions.',
        'D - High Risk': 'High risk profile. Detailed underwriter review needed.',
        'E - Very High Risk': 'Very high risk. Likely rejection or very high premium.'
    }
    return mapping.get(band, 'Manual review required.')
