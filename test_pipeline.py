"""Quick pipeline test - run with: python test_pipeline.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.pipeline import run_pipeline

test_cases = [
    {
        'name': 'Low Risk Applicant',
        'data': {'full_name': 'Rahul Sharma', 'age': 32, 'gender': 'Male', 'mobile': '9876543210',
                 'email': 'rahul@test.com', 'occupation': 'engineer', 'employment_status': 'employed',
                 'annual_income': 900000, 'credit_score': 780, 'existing_loans': 1, 'previous_claims': 0,
                 'insurance_type': 'life', 'address': 'Bangalore', 'documents': {}}
    },
    {
        'name': 'High Risk Applicant',
        'data': {'full_name': 'Vikram Singh', 'age': 55, 'gender': 'Male', 'mobile': '9543210987',
                 'email': 'vikram@test.com', 'occupation': 'unemployed', 'employment_status': 'unemployed',
                 'annual_income': 120000, 'credit_score': 520, 'existing_loans': 6, 'previous_claims': 5,
                 'insurance_type': 'health', 'address': 'Delhi', 'documents': {}}
    }
]

for tc in test_cases:
    print(f"\n{'='*50}")
    print(f"Testing: {tc['name']}")
    result = run_pipeline(tc['data'])
    print(f"  Decision:      {result['decision']['final_decision']}")
    print(f"  Confidence:    {result['decision']['confidence']:.0%}")
    print(f"  Risk Score:    {result['risk_score']['composite_score']}/100")
    print(f"  Risk Band:     {result['risk_score']['risk_band']}")
    print(f"  Fraud Score:   {result['fraud_detection']['fraud_score']}/100")
    print(f"  Financial Risk:{result['financial_risk']['risk_level']}")
    if result['premium']['status'] == 'Calculated':
        print(f"  Annual Premium: Rs.{result['premium']['annual_premium']:,.0f}")
    print(f"  Report ID:     {result['report']['report_id']}")

print("\n✅ All pipeline tests passed!")
