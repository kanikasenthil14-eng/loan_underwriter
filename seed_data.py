"""
Seed script — populates MongoDB with sample applications for demo/testing.
Run: python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from run import app
from app import mongo, bcrypt
from app.models.application_model import application_schema
from app.utils.pipeline import run_pipeline
from datetime import datetime, timedelta
import random

SAMPLE_APPLICANTS = [
    {'full_name': 'Rahul Sharma', 'age': 32, 'gender': 'Male', 'mobile': '9876543210',
     'email': 'rahul@example.com', 'occupation': 'engineer', 'employment_status': 'employed',
     'annual_income': 850000, 'credit_score': 780, 'existing_loans': 1, 'previous_claims': 0,
     'address': '12 MG Road, Bangalore', 'insurance_type': 'life'},

    {'full_name': 'Priya Patel', 'age': 28, 'gender': 'Female', 'mobile': '9765432109',
     'email': 'priya@example.com', 'occupation': 'doctor', 'employment_status': 'employed',
     'annual_income': 1200000, 'credit_score': 820, 'existing_loans': 0, 'previous_claims': 0,
     'address': '45 Park Street, Mumbai', 'insurance_type': 'health'},

    {'full_name': 'Amit Kumar', 'age': 45, 'gender': 'Male', 'mobile': '9654321098',
     'email': 'amit@example.com', 'occupation': 'self-employed', 'employment_status': 'self-employed',
     'annual_income': 350000, 'credit_score': 620, 'existing_loans': 3, 'previous_claims': 2,
     'address': '78 Civil Lines, Delhi', 'insurance_type': 'health'},

    {'full_name': 'Sunita Reddy', 'age': 55, 'gender': 'Female', 'mobile': '9543210987',
     'email': 'sunita@example.com', 'occupation': 'government employee', 'employment_status': 'employed',
     'annual_income': 600000, 'credit_score': 710, 'existing_loans': 1, 'previous_claims': 1,
     'address': '23 Jubilee Hills, Hyderabad', 'insurance_type': 'life'},

    {'full_name': 'Vikram Singh', 'age': 38, 'gender': 'Male', 'mobile': '9432109876',
     'email': 'vikram@example.com', 'occupation': 'freelancer', 'employment_status': 'self-employed',
     'annual_income': 180000, 'credit_score': 580, 'existing_loans': 5, 'previous_claims': 3,
     'address': '56 Anna Nagar, Chennai', 'insurance_type': 'vehicle'},

    {'full_name': 'Meera Joshi', 'age': 26, 'gender': 'Female', 'mobile': '9321098765',
     'email': 'meera@example.com', 'occupation': 'teacher', 'employment_status': 'employed',
     'annual_income': 420000, 'credit_score': 740, 'existing_loans': 0, 'previous_claims': 0,
     'address': '89 Koregaon Park, Pune', 'insurance_type': 'health'},
]

def seed():
    with app.app_context():
        # Create sample customer users
        for applicant in SAMPLE_APPLICANTS:
            email = applicant['email']
            if not mongo.db.users.find_one({'email': email}):
                hashed = bcrypt.generate_password_hash('Test@123').decode('utf-8')
                mongo.db.users.insert_one({
                    'name': applicant['full_name'],
                    'email': email,
                    'mobile': applicant['mobile'],
                    'password': hashed,
                    'role': 'customer',
                    'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 60))
                })

            user = mongo.db.users.find_one({'email': email})
            user_id = str(user['_id'])

            # Create application
            app_doc = application_schema(user_id, applicant, {})
            app_doc['submitted_at'] = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            result = mongo.db.applications.insert_one(app_doc)
            app_id = result.inserted_id

            # Run pipeline
            try:
                app_doc['_id'] = app_id
                enriched = run_pipeline(app_doc)
                enriched['status'] = 'processed'
                enriched['updated_at'] = datetime.utcnow()
                update_data = {k: v for k, v in enriched.items() if k != '_id'}
                mongo.db.applications.update_one({'_id': app_id}, {'$set': update_data})
                print(f"✓ Processed: {applicant['full_name']} → {enriched.get('decision', {}).get('final_decision', 'N/A')}")
            except Exception as e:
                print(f"✗ Error for {applicant['full_name']}: {e}")

        print("\n✅ Seed data loaded successfully!")
        print("Customer login: any sample email above / password: Test@123")
        print("Admin login: admin@insurance.com / Admin@123")

if __name__ == '__main__':
    seed()
