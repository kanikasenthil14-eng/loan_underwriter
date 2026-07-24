# Agentic AI for End-to-End Insurance Underwriting

A full-stack AI-powered insurance underwriting platform with 7 AI agents, Random Forest ML, fraud detection, and real-time risk scoring.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js |
| Backend | Python Flask |
| Database | MongoDB |
| ML Model | Scikit-learn (Random Forest) |
| OCR | EasyOCR |
| Auth | Flask-Login + Flask-Bcrypt |
| Export | CSV (Tableau-ready) |

## Project Structure

```
insurance_underwriting/
├── run.py                          # App entry point
├── config.py                       # Configuration
├── seed_data.py                    # Sample data loader
├── requirements.txt
├── .env                            # Environment variables
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── agents/
│   │   ├── document_verification_agent.py
│   │   ├── financial_risk_agent.py
│   │   ├── fraud_detection_agent.py
│   │   ├── risk_scoring_agent.py
│   │   ├── decision_agent.py
│   │   ├── premium_calculation_agent.py
│   │   └── report_generation_agent.py
│   ├── ml/
│   │   ├── train_model.py          # Train Random Forest
│   │   └── predictor.py           # ML inference
│   ├── models/
│   │   ├── user_model.py
│   │   └── application_model.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── customer_routes.py
│   │   ├── admin_routes.py
│   │   └── api_routes.py
│   └── utils/
│       ├── pipeline.py             # AI agent orchestrator
│       └── helpers.py             # File upload, CSV export
├── templates/
│   ├── base.html
│   ├── auth/
│   │   ├── landing.html
│   │   ├── login.html
│   │   └── register.html
│   ├── customer/
│   │   ├── layout.html
│   │   ├── dashboard.html
│   │   ├── apply.html
│   │   ├── application_detail.html
│   │   └── report.html
│   └── admin/
│       ├── layout.html
│       ├── dashboard.html
│       ├── applications.html
│       ├── application_detail.html
│       └── users.html
└── static/
    ├── css/main.css
    ├── js/
    │   ├── main.js
    │   └── apply.js
    └── uploads/
```

## Installation

### Prerequisites
- Python 3.9+
- MongoDB (running on localhost:27017)
- pip

### Setup

```bash
# 1. Navigate to project
cd insurance_underwriting

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
# Edit .env file with your settings

# 5. Train the ML model
python -m app.ml.train_model

# 6. Load sample data (optional)
python seed_data.py

# 7. Run the application
python run.py
```

Open: http://localhost:5000

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@insurance.com | Admin@123 |
| Customer (sample) | rahul@example.com | Test@123 |

## AI Agent Pipeline

```
Application Submitted
        ↓
1. Document Verification Agent  (OCR + rule-based)
        ↓
2. Financial Risk Assessment Agent  (income, credit, employment)
        ↓
3. Fraud Detection Agent  (pattern analysis)
        ↓
4. ML Prediction  (Random Forest)
        ↓
5. Risk Scoring Agent  (composite score)
        ↓
6. Decision Agent  (Approved / Manual Review / Rejected)
        ↓
7. Premium Calculation Agent
        ↓
8. Report Generation Agent
        ↓
   Stored in MongoDB
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check |
| GET | /api/applications | List applications |
| GET | /api/applications/:id | Get application |
| GET | /api/stats | Dashboard stats (admin) |
| POST | /api/applications/:id/reprocess | Reprocess application |

## Tableau Integration

Export data via Admin Dashboard → Export CSV button.
The CSV includes all underwriting fields compatible with Tableau for BI dashboards.

## Features

### Customer
- Register/Login
- Multi-step application form
- Document upload (Aadhaar, PAN, Income Proof)
- Real-time AI processing
- View decision with risk breakdown
- Download PDF report

### Admin
- Analytics dashboard with Chart.js
- All applications with search/filter
- Decision override with audit trail
- User management
- CSV export for Tableau
- REST API access
