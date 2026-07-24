"""
Underwriting Pipeline - orchestrates all AI agents in sequence.
"""
from app.agents import (
    document_verification_agent,
    financial_risk_agent,
    fraud_detection_agent,
    risk_scoring_agent,
    decision_agent,
    premium_calculation_agent,
    report_generation_agent
)
from app.ml.predictor import predict as ml_predict

def run_pipeline(application_data):
    """
    Run the full underwriting pipeline.
    Returns enriched application_data with all agent results.
    """
    data = dict(application_data)

    # Step 1: Document Verification
    data['doc_verification'] = document_verification_agent.run(data)

    # Step 2: Financial Risk Assessment
    data['financial_risk'] = financial_risk_agent.run(data)

    # Step 3: Fraud Detection (uses doc verification results)
    data['fraud_detection'] = fraud_detection_agent.run(data)

    # Step 4: ML Prediction
    doc_score = data['doc_verification'].get('score', 80)
    fraud_score = data['fraud_detection'].get('fraud_score', 0)
    data['ml_prediction'] = ml_predict(data, doc_score=doc_score, fraud_score=fraud_score)

    # Step 5: Risk Scoring (composite)
    data['risk_score'] = risk_scoring_agent.run(data)

    # Step 6: Decision
    data['decision'] = decision_agent.run(data)

    # Step 7: Loan Terms Calculation
    data['premium'] = premium_calculation_agent.run(data)

    # Step 8: Report Generation
    data['report'] = report_generation_agent.run(data)

    return data
