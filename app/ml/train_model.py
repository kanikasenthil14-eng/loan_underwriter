"""
Train Random Forest model for loan approval decisions.
Run this script once to generate the model file.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

LABELS = ['Approved', 'Manual Review', 'Rejected']

def generate_training_data(n=2000):
    """Generate synthetic loan approval training data."""
    np.random.seed(42)
    data = {
        'age': np.random.randint(18, 75, n),
        'annual_income': np.random.randint(100000, 3000000, n),
        'credit_score': np.random.randint(300, 900, n),
        'existing_loans': np.random.randint(0, 8, n),
        'loan_amount': np.random.randint(50000, 5000000, n),
        'loan_tenure': np.random.randint(6, 360, n),
        'employment_encoded': np.random.randint(0, 5, n),
        'doc_score': np.random.randint(40, 100, n),
        'fraud_score': np.random.randint(0, 80, n),
    }
    df = pd.DataFrame(data)

    def label_row(row):
        score = 0
        if row['credit_score'] < 600: score += 30
        elif row['credit_score'] < 700: score += 15
        if row['annual_income'] < 200000: score += 25
        elif row['annual_income'] < 400000: score += 10
        if row['existing_loans'] > 4: score += 20
        # Debt-to-income ratio
        monthly_income = row['annual_income'] / 12
        emi_estimate = row['loan_amount'] / row['loan_tenure']
        if emi_estimate > monthly_income * 0.5: score += 20
        if row['employment_encoded'] == 4: score += 20
        if row['doc_score'] < 60: score += 25
        if row['fraud_score'] > 50: score += 30
        if row['age'] < 20 or row['age'] > 65: score += 10

        if score >= 70: return 'Rejected'
        if score >= 35: return 'Manual Review'
        return 'Approved'

    df['decision'] = df.apply(label_row, axis=1)
    return df

def train():
    print("Generating training data...")
    df = generate_training_data(2000)

    feature_cols = ['age', 'annual_income', 'credit_score', 'existing_loans',
                    'loan_amount', 'loan_tenure', 'employment_encoded', 'doc_score', 'fraud_score']
    X = df[feature_cols]
    y = df['decision']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs('app/ml', exist_ok=True)
    joblib.dump(model, 'app/ml/underwriting_model.pkl')
    joblib.dump(feature_cols, 'app/ml/feature_columns.pkl')
    print("Model saved to app/ml/underwriting_model.pkl")
    return model, feature_cols

if __name__ == '__main__':
    train()
