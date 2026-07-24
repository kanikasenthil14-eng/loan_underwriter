"""
Loan Terms Agent
Calculates EMI, interest rate, and loan terms based on risk score and applicant profile.
"""

def run(application_data):
    """Calculate loan terms based on risk and applicant profile."""
    decision = application_data.get('decision', {})
    risk_score = application_data.get('risk_score', {})
    annual_income = float(application_data.get('annual_income', 300000))
    age = int(application_data.get('age', 30))
    loan_amount = float(application_data.get('loan_amount', 0))
    loan_tenure = int(application_data.get('loan_tenure', 12))
    loan_purpose = application_data.get('loan_purpose', 'personal').lower()
    final_decision = decision.get('final_decision', 'Manual Review')

    if final_decision == 'Rejected':
        return {
            'loan_amount': 0, 'emi': 0, 'interest_rate': 0,
            'total_payable': 0, 'tenure_months': 0,
            'status': 'Not Applicable - Loan Rejected',
            'agent': 'Loan Terms Agent'
        }

    composite_score = float(risk_score.get('composite_score', 50))
    interest_rate = _interest_rate(composite_score, loan_purpose)
    age_adjustment = _age_adjustment(age)
    final_rate = round(interest_rate + age_adjustment, 2)

    # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    monthly_rate = final_rate / (12 * 100)
    if monthly_rate > 0:
        emi = loan_amount * monthly_rate * (1 + monthly_rate) ** loan_tenure / ((1 + monthly_rate) ** loan_tenure - 1)
    else:
        emi = loan_amount / loan_tenure

    total_payable = round(emi * loan_tenure, 2)
    total_interest = round(total_payable - loan_amount, 2)

    return {
        'loan_amount': loan_amount,
        'interest_rate': final_rate,
        'tenure_months': loan_tenure,
        'emi': round(emi, 2),
        'total_payable': total_payable,
        'total_interest': total_interest,
        'loan_purpose': loan_purpose.title(),
        'status': 'Calculated',
        'agent': 'Loan Terms Agent'
    }

def _interest_rate(score, purpose):
    purpose_base = {'home': 8.5, 'education': 9.0, 'vehicle': 10.0, 'business': 11.0, 'personal': 12.0}
    base = purpose_base.get(purpose, 12.0)
    if score <= 25: return base
    if score <= 40: return base + 1.5
    if score <= 55: return base + 3.0
    if score <= 70: return base + 5.0
    return base + 7.0

def _age_adjustment(age):
    if age < 25: return 1.0
    if age <= 45: return 0.0
    if age <= 55: return 0.5
    return 1.5
