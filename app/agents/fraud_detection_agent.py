"""
Fraud Detection Agent
Detects suspicious patterns, inconsistencies, and potential fraud indicators.
"""
import re

def run(application_data):
    """Detect fraud signals in the application."""
    flags = []
    fraud_score = 0

    annual_income = float(application_data.get('annual_income', 0))
    credit_score = int(application_data.get('credit_score', 300))
    age = int(application_data.get('age', 0))
    employment_status = application_data.get('employment_status', '').lower()
    existing_loans = int(application_data.get('existing_loans', 0))
    loan_amount = float(application_data.get('loan_amount', 0))
    email = application_data.get('email', '')
    mobile = application_data.get('mobile', '')
    doc_verification = application_data.get('doc_verification', {})

    # Check 1: Income vs Employment inconsistency
    if employment_status == 'unemployed' and annual_income > 500000:
        flags.append('High income reported despite unemployed status')
        fraud_score += 25

    # Check 2: Unrealistic credit score
    if credit_score > 900 or credit_score < 300:
        flags.append(f'Unusual credit score: {credit_score}')
        fraud_score += 20

    # Check 3: Age anomalies
    if age < 18 or age > 80:
        flags.append(f'Unusual age: {age}')
        fraud_score += 15

    # Check 4: Excessive existing loans with loan amount
    if existing_loans > 3 and annual_income < 300000:
        flags.append('Multiple existing loans with very low income')
        fraud_score += 20

    # Check 5: Loan amount too high relative to income
    loan_amount = float(application_data.get('loan_amount', 0))
    if loan_amount > annual_income * 10 and annual_income > 0:
        flags.append('Requested loan amount is unusually high relative to income')
        fraud_score += 20

    # Check 6: Document verification failures
    doc_score = doc_verification.get('score', 100)
    if doc_score < 50:
        flags.append('Document verification score critically low')
        fraud_score += 25
    elif doc_score < 70:
        flags.append('Document verification raised concerns')
        fraud_score += 10

    # Check 7: Suspicious email patterns
    if _is_suspicious_email(email):
        flags.append('Suspicious email pattern detected')
        fraud_score += 10

    # Check 8: Mobile number validation
    if not _valid_mobile(mobile):
        flags.append('Invalid mobile number format')
        fraud_score += 5

    # Check 9: Income round number suspicion (very round numbers)
    if annual_income > 0 and annual_income % 100000 == 0 and annual_income > 1000000:
        flags.append('Suspiciously round income figure')
        fraud_score += 5

    fraud_score = min(fraud_score, 100)
    risk_level = _fraud_risk_level(fraud_score)

    return {
        'fraud_score': fraud_score,
        'risk_level': risk_level,
        'flags': flags,
        'is_suspicious': fraud_score >= 40,
        'recommendation': _fraud_recommendation(risk_level),
        'agent': 'Fraud Detection Agent'
    }

def _is_suspicious_email(email):
    suspicious_patterns = [r'test@', r'fake@', r'dummy@', r'xxx@', r'temp@']
    return any(re.search(p, email.lower()) for p in suspicious_patterns)

def _valid_mobile(mobile):
    return bool(re.match(r'^[6-9]\d{9}$', str(mobile).strip()))

def _fraud_risk_level(score):
    if score < 20: return 'Low'
    if score < 40: return 'Medium'
    if score < 70: return 'High'
    return 'Critical'

def _fraud_recommendation(level):
    mapping = {
        'Low': 'No significant fraud indicators. Proceed normally.',
        'Medium': 'Minor inconsistencies found. Verify key details.',
        'High': 'Multiple fraud indicators. Manual investigation required.',
        'Critical': 'Critical fraud risk. Reject or escalate immediately.'
    }
    return mapping.get(level, 'Manual review required.')
