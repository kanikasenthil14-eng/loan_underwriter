"""
Financial Risk Assessment Agent
Analyzes income, occupation, employment status, credit score, and loan burden.
"""

OCCUPATION_RISK = {
    'government employee': 1, 'doctor': 2, 'engineer': 2, 'teacher': 1,
    'lawyer': 2, 'accountant': 2, 'nurse': 2, 'banker': 2,
    'self-employed': 4, 'business owner': 3, 'freelancer': 4,
    'driver': 4, 'construction worker': 5, 'farmer': 4,
    'student': 3, 'retired': 3, 'unemployed': 6, 'other': 4
}

def run(application_data):
    """Assess financial risk based on applicant's financial profile."""
    annual_income = float(application_data.get('annual_income', 0))
    credit_score = int(application_data.get('credit_score', 300))
    existing_loans = int(application_data.get('existing_loans', 0))
    loan_amount = float(application_data.get('loan_amount', 0))
    employment_status = application_data.get('employment_status', 'unemployed').lower()
    occupation = application_data.get('occupation', 'other').lower()
    age = int(application_data.get('age', 30))

    risk_factors = {}
    total_risk = 0

    # Income risk (0-25 points)
    income_risk = _income_risk(annual_income)
    risk_factors['income_risk'] = income_risk
    total_risk += income_risk

    # Credit score risk (0-25 points)
    credit_risk = _credit_risk(credit_score)
    risk_factors['credit_risk'] = credit_risk
    total_risk += credit_risk

    # Employment risk (0-20 points)
    emp_risk = _employment_risk(employment_status)
    risk_factors['employment_risk'] = emp_risk
    total_risk += emp_risk

    # Occupation risk (0-15 points)
    occ_level = OCCUPATION_RISK.get(occupation, 4)
    occ_risk = round((occ_level / 6) * 15, 2)
    risk_factors['occupation_risk'] = occ_risk
    total_risk += occ_risk

    # Loan burden risk (0-10 points)
    loan_risk = min(existing_loans * 2.5, 10)
    risk_factors['loan_risk'] = loan_risk
    total_risk += loan_risk

    # Debt-to-income ratio risk (0-5 points)
    monthly_income = annual_income / 12 if annual_income > 0 else 1
    dti = (loan_amount / 12) / monthly_income if loan_amount > 0 else 0
    dti_risk = min(dti * 10, 5)
    risk_factors['dti_risk'] = round(dti_risk, 2)
    total_risk += dti_risk

    total_risk = round(min(total_risk, 100), 2)
    risk_level = _classify_risk(total_risk)

    return {
        'total_risk_score': total_risk,
        'risk_level': risk_level,
        'risk_factors': risk_factors,
        'income_category': _income_category(annual_income),
        'credit_category': _credit_category(credit_score),
        'recommendation': _recommendation(risk_level),
        'agent': 'Financial Risk Assessment Agent'
    }

def _income_risk(income):
    if income >= 1500000: return 0
    if income >= 800000: return 5
    if income >= 400000: return 10
    if income >= 200000: return 18
    return 25

def _credit_risk(score):
    if score >= 750: return 0
    if score >= 700: return 5
    if score >= 650: return 10
    if score >= 600: return 18
    return 25

def _employment_risk(status):
    mapping = {'employed': 0, 'self-employed': 10, 'part-time': 12, 'contract': 8, 'unemployed': 20}
    return mapping.get(status, 15)

def _income_category(income):
    if income >= 1500000: return 'High Income'
    if income >= 600000: return 'Middle Income'
    if income >= 200000: return 'Low Income'
    return 'Very Low Income'

def _credit_category(score):
    if score >= 750: return 'Excellent'
    if score >= 700: return 'Good'
    if score >= 650: return 'Fair'
    if score >= 600: return 'Poor'
    return 'Very Poor'

def _classify_risk(score):
    if score <= 25: return 'Low'
    if score <= 50: return 'Medium'
    if score <= 75: return 'High'
    return 'Very High'

def _recommendation(risk_level):
    mapping = {
        'Low': 'Application looks financially sound. Recommend approval.',
        'Medium': 'Moderate financial risk. Standard underwriting review advised.',
        'High': 'High financial risk detected. Detailed manual review required.',
        'Very High': 'Very high financial risk. Consider rejection or high premium.'
    }
    return mapping.get(risk_level, 'Manual review required.')
