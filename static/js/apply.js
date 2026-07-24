// InsureAI — Application Form Multi-Step Logic

let currentStep = 1;
const totalSteps = 4;

function nextStep(step) {
    if (!validateStep(step)) return;
    document.getElementById(`step-${step}`).classList.add('d-none');
    document.getElementById(`step-${step + 1}`).classList.remove('d-none');
    currentStep = step + 1;
    updateStepIndicators();
    if (currentStep === 4) buildReviewSummary();
}

function prevStep(step) {
    document.getElementById(`step-${step}`).classList.add('d-none');
    document.getElementById(`step-${step - 1}`).classList.remove('d-none');
    currentStep = step - 1;
    updateStepIndicators();
}

function validateStep(step) {
    const stepEl = document.getElementById(`step-${step}`);
    const required = stepEl.querySelectorAll('[required]');
    let valid = true;
    required.forEach(field => {
        const empty = field.value === '' || (field.tagName === 'SELECT' && field.value === '');
        if (empty) {
            field.classList.add('is-invalid');
            valid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    if (!valid) {
        showNotification('Please fill in all required fields.', 'warning');
    }
    return valid;
}

function updateStepIndicators() {
    for (let i = 1; i <= totalSteps; i++) {
        const indicator = document.getElementById(`step-indicator-${i}`);
        if (!indicator) continue;
        indicator.classList.remove('active', 'completed');
        if (i < currentStep) indicator.classList.add('completed');
        else if (i === currentStep) indicator.classList.add('active');
    }
}

function buildReviewSummary() {
    const form = document.getElementById('applicationForm');
    const data = new FormData(form);
    const container = document.getElementById('reviewSummary');
    if (!container) return;

    const fields = [
        ['Full Name', 'full_name'], ['Age', 'age'], ['Gender', 'gender'],
        ['Email', 'email'], ['Mobile', 'mobile'], ['Loan Purpose', 'loan_purpose'],
        ['Occupation', 'occupation'], ['Employment Status', 'employment_status'],
        ['Annual Income', 'annual_income'], ['Credit Score', 'credit_score'],
        ['Loan Amount', 'loan_amount'], ['Loan Tenure (months)', 'loan_tenure'], ['Existing Loans', 'existing_loans']
    ];

    container.innerHTML = fields.map(([label, key]) => {
        const val = data.get(key) || '—';
        return `<div class="col-md-4 col-6">
            <div class="info-item">
                <div class="info-label">${label}</div>
                <div class="info-value">${val}</div>
            </div>
        </div>`;
    }).join('');
}

function showPreview(input, previewId, zoneId) {
    const preview = document.getElementById(previewId);
    const zone = document.getElementById(zoneId);
    if (input.files && input.files[0]) {
        const file = input.files[0];
        preview.innerHTML = `<div class="text-success small mt-1"><i class="fas fa-check-circle me-1"></i>${file.name}</div>`;
        zone.classList.add('has-file');
    }
}

function showNotification(message, type = 'info') {
    const container = document.querySelector('.toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-bg-${type} border-0`;
    toast.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function createToastContainer() {
    const c = document.createElement('div');
    c.className = 'toast-container position-fixed top-0 end-0 p-3';
    c.style.zIndex = '9999';
    document.body.appendChild(c);
    return c;
}

// Show loading modal on form submit without blocking the request
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('applicationForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingModal = document.getElementById('loadingModal');

    if (!form) return;

    form.addEventListener('submit', () => {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
        }

        if (loadingModal) {
            loadingModal.classList.remove('d-none');
            loadingModal.style.display = 'block';
            const steps = document.querySelectorAll('.agent-step');
            steps.forEach((step, i) => {
                setTimeout(() => {
                    const icon = step.querySelector('i');
                    const label = step.querySelector('span');
                    if (icon) icon.className = 'fas fa-check-circle text-success me-2';
                    if (label) label.style.color = '#22c55e';
                }, (i + 1) * 800);
            });
        }
    });
});
