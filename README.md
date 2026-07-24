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

## Deployment

This repository includes deployment automation for Docker, GitHub Container Registry (GHCR), and Render.

Overview of the recommended flow
- Build a Docker image for the app and push it to GHCR.
- Configure a Render Web Service to deploy either from the GitHub repo (Render builds) or pull the image from GHCR.
- Use the included GitHub Actions workflow to automate build, push, and trigger Render deploys.

Required preparatory steps
- Ensure the ML model artifact exists before creating production images. Locally run:

```bash
python -m app.ml.train_model
git add app/ml/*.joblib || true
git commit -m "Add trained model for deployment" || true
git push origin main
```

- Use a managed MongoDB for production (MongoDB Atlas) and obtain the connection string `MONGO_URI`.

- Create these GitHub repository secrets (Settings → Secrets → Actions):
        - `RENDER_API_KEY` — Render service API key (for triggering deploys)
        - `RENDER_SERVICE_ID` — Render service id (the service to trigger)
        - (optional) `GHCR_PAT` — personal access token with `packages:write` if you prefer a PAT instead of `GITHUB_TOKEN`

Local Docker (quick test)

```bash
# build and run locally (exposes port 8000)
docker build -t insureai:local .
docker run --rm -p 8000:8000 \
        -e MONGO_URI="mongodb://host.docker.internal:27017/insurance" \
        -e SECRET_KEY="changeme" \
        -e ADMIN_EMAIL="admin@insurance.com" \
        -e ADMIN_PASSWORD="Admin@123" \
        insureai:local
```

Automated CI/CD (GH Actions → GHCR → Render)

1. The repository already contains the workflow `.github/workflows/ghcr-render-deploy.yml` which on push to `main` will:
         - Build and push the Docker image to GHCR at `ghcr.io/<owner>/<repo>:latest`.
         - Trigger a redeploy on Render using the Render Deploys API.

2. Configure the workflow secrets in GitHub as noted above. If GHCR push fails using the built-in `GITHUB_TOKEN`, create a `GHCR_PAT` and update the workflow to use it.

Render service configuration

- Option A (Render builds from repo) — easiest:
        - Create a new Web Service in Render and connect your GitHub repo.
        - Environment: Docker
        - Build Command: leave empty (Render uses your Dockerfile)
        - Start Command: `gunicorn -w 4 -b 0.0.0.0:8000 run:app`
        - Set Environment Variables in the Render dashboard (or in `render.yaml`):
                - `MONGO_URI`, `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `UPLOAD_FOLDER` (set to `/opt/render/project/src/static/uploads`)

- Option B (Render pulls from GHCR image):
        - Push to GHCR (workflow does this). In Render, create a Web Service from Private Docker Registry and point it to `ghcr.io/<owner>/<repo>:latest`.
        - Provide registry credentials if the image is private (username = GitHub username, password = GHCR PAT).

Notes about `render.yaml`:
- `render.yaml` in the repo is a template that you can import into Render; edit the `repo` field and optional `dockerImage` field before importing.

Verifying the deployment

1. After a successful deploy, open the Render service URL. The health endpoint is available at `/api/health`.

```bash
curl https://<your-render-url>/api/health
```

Expected response: a small JSON confirming the app is alive.

2. Check Render logs (Dashboard → Logs) for errors during startup. Common issues:
         - Missing `MONGO_URI` or incorrect credentials.
         - ML model file not present: create/train the model and commit it before building the image or configure the Docker build to train during image build (not recommended for long training jobs).

3. Run a quick end-to-end smoke test (replace values):

```bash
# register a test user (example)
curl -X POST https://<your-render-url>/auth/register -d "email=test@example.com&password=Test@123"

# submit a minimal application via your app UI or the API
```

4. If using the GitHub Actions workflow, check Actions → ghcr-render-deploy for build logs and the final step that triggers Render.

Troubleshooting
- If GHCR push fails, inspect the Actions logs for authentication errors; add `GHCR_PAT` and update the login step to use it.
- If Render build fails, check the Build and Service logs to see Docker build errors; common fixes are missing system packages or incompatible Python wheels (add `buildpack` or system deps in the Dockerfile).

Security
- Never commit secrets to the repo. Use GitHub Secrets and Render environment variables.

Production recommendations
- Use MongoDB Atlas for reliability.
- Store uploaded documents in S3 or Azure Blob; Render's disk is not suitable for large or shared storage.
- Store trained ML artifacts in object storage and load them during startup.



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
