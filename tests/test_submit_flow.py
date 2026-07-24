import unittest

from app import create_app


class SubmitFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True, SECRET_KEY='test-secret')
        self.client = self.app.test_client()

    def test_submit_flow_with_fallback_store(self):
        register_response = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'mobile': '9876543210',
            'password': 'Pass1234!',
            'confirm_password': 'Pass1234!'
        }, follow_redirects=True)
        self.assertEqual(register_response.status_code, 200)

        login_response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'Pass1234!'
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        apply_page = self.client.get('/customer/apply')
        self.assertEqual(apply_page.status_code, 200)
        self.assertIn('form="applicationForm"', apply_page.get_data(as_text=True))

        submit_response = self.client.post('/customer/apply', data={
            'full_name': 'Test Applicant',
            'age': '30',
            'gender': 'Male',
            'email': 'test@example.com',
            'mobile': '9876543210',
            'loan_purpose': 'personal',
            'address': '123 Test Street',
            'occupation': 'Engineer',
            'employment_status': 'employed',
            'annual_income': '500000',
            'credit_score': '700',
            'loan_amount': '200000',
            'loan_tenure': '24',
            'existing_loans': '0',
            'loan_type': 'personal'
        }, follow_redirects=True)

        self.assertEqual(submit_response.status_code, 200)
        self.assertIn('Application submitted', submit_response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
