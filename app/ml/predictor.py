"""
ML Predictor - loads trained Random Forest model and makes predictions.
"""
import os
import joblib
import numpy as np

_model = None
_features = None

EMPLOYMENT_MAP = {'employed': 0, 'self-employed': 1, 'part-time': 2, 'contract': 3, 'unemployed': 4}

def _load_model():
    global _model, _features
    if _model is None:
        model_path = os.path.join(os.path.dirname(__file__), 'underwriting_model.pkl')
        feat_path = os.path.join(os.path.dirname(__file__), 'feature_columns.pkl')
        if os.path.exists(model_path):
            _model = joblib.load(model_path)
            _features = joblib.load(feat_path)
        else:
            # Train model on first run if not exists
            from app.ml.train_model import train
            _model, _features = train()
    return _model, _features

def predict(application_data, doc_score=80, fraud_score=0):
    """Run ML prediction on application data."""
    model, features = _load_model()

    emp_encoded = EMPLOYMENT_MAP.get(
        application_data.get('employment_status', 'employed').lower(), 0
    )

    import pandas as pd
    feature_vector = pd.DataFrame([[
        int(application_data.get('age', 30)),
        float(application_data.get('annual_income', 300000)),
        int(application_data.get('credit_score', 650)),
        int(application_data.get('existing_loans', 0)),
        float(application_data.get('loan_amount', 100000)),
        int(application_data.get('loan_tenure', 12)),
        emp_encoded,
        float(doc_score),
        float(fraud_score)
    ]], columns=features)

    prediction = model.predict(feature_vector)[0]
    probabilities = model.predict_proba(feature_vector)[0]
    classes = model.classes_
    confidence = float(max(probabilities))

    prob_dict = {cls: round(float(prob), 4) for cls, prob in zip(classes, probabilities)}

    return {
        'decision': prediction,
        'confidence': round(confidence, 4),
        'probabilities': prob_dict,
        'features_count': len(features),
        'model': 'Random Forest Classifier'
    }
