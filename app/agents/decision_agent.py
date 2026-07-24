"""
Decision Agent
Makes final underwriting decision based on ML prediction and risk scores.
"""

def run(application_data):
    """Determine final underwriting decision."""
    ml_prediction = application_data.get('ml_prediction', {})
    risk_score = application_data.get('risk_score', {})
    fraud = application_data.get('fraud_detection', {})
    doc_ver = application_data.get('doc_verification', {})
    financial = application_data.get('financial_risk', {})

    ml_decision = ml_prediction.get('decision', 'Manual Review')
    ml_confidence = float(ml_prediction.get('confidence', 0.5))
    composite_score = float(risk_score.get('composite_score', 50))
    fraud_score = float(fraud.get('fraud_score', 0))
    doc_status = doc_ver.get('status', 'failed')
    fraud_flags = fraud.get('flags', [])
    doc_issues = doc_ver.get('issues', [])
    financial_risk_level = financial.get('risk_level', 'Medium')

    reasons = []

    if fraud_score >= 70:
        final_decision = 'Rejected'
        reasons.append(f'Critical fraud risk score of {fraud_score}/100 detected')
        if fraud_flags:
            reasons += [f'Fraud flag: {f}' for f in fraud_flags]
        confidence = 0.95

    elif doc_status == 'failed':
        final_decision = 'Rejected'
        reasons.append('Document verification failed')
        if doc_issues:
            reasons += [f'Document issue: {i}' for i in doc_issues]
        confidence = 0.90

    elif fraud_score >= 40 or composite_score >= 75:
        final_decision = 'Manual Review'
        if fraud_score >= 40:
            reasons.append(f'Elevated fraud score of {fraud_score}/100 requires investigation')
        if composite_score >= 75:
            reasons.append(f'High composite risk score of {composite_score}/100')
        reasons.append('Application flagged for human review')
        confidence = 0.80

    elif ml_confidence >= 0.75:
        final_decision = ml_decision
        if final_decision == 'Approved':
            reasons.append(f'ML model approved with {ml_confidence:.0%} confidence')
            reasons.append(f'Financial risk level: {financial_risk_level}')
            reasons.append(f'Composite risk score: {composite_score}/100')
            if fraud_score < 20:
                reasons.append('No significant fraud indicators detected')
        elif final_decision == 'Rejected':
            reasons.append(f'ML model rejected with {ml_confidence:.0%} confidence')
            reasons.append(f'Composite risk score: {composite_score}/100 exceeds threshold')
            reasons.append(f'Financial risk level: {financial_risk_level}')
        else:
            reasons.append(f'ML model flagged for review with {ml_confidence:.0%} confidence')
        confidence = ml_confidence

    else:
        final_decision = 'Manual Review'
        reasons.append(f'ML model confidence too low ({ml_confidence:.0%}) for auto-decision')
        reasons.append('Manual underwriter review required')
        confidence = 0.60

    conditions = _get_conditions(final_decision, composite_score, fraud_score)
    primary_reason = reasons[0] if reasons else 'Decision based on risk analysis'

    return {
        'final_decision': final_decision,
        'reason': primary_reason,
        'detailed_reasons': reasons,
        'confidence': round(confidence, 3),
        'conditions': conditions,
        'ml_input': ml_decision,
        'override_applied': final_decision != ml_decision,
        'agent': 'Decision Agent'
    }

def _get_conditions(decision, risk_score, fraud_score):
    conditions = []
    if decision == 'Approved':
        if risk_score > 40:
            conditions.append('Higher interest rate applicable due to elevated risk')
        if risk_score > 30:
            conditions.append('Collateral or guarantor may be required')
        conditions.append('Standard loan terms apply')
    elif decision == 'Manual Review':
        conditions.append('Additional documentation may be required')
        conditions.append('Loan officer will contact within 3-5 business days')
        if fraud_score > 20:
            conditions.append('Identity verification call scheduled')
    elif decision == 'Rejected':
        conditions.append('Application does not meet loan eligibility criteria')
        conditions.append('Reapplication allowed after 6 months with improved credit profile')
    return conditions
