"""
Document Verification Agent
Validates uploaded documents using EasyOCR and rule-based checks.
"""
import os
import re

def run(application_data):
    """
    Verifies uploaded documents for authenticity and completeness.
    Returns verification result dict.
    """
    documents = application_data.get('documents', {})
    full_name = application_data.get('full_name', '').lower()
    issues = []
    verified_docs = {}
    score = 100  # Start with perfect score, deduct for issues

    for doc_type, doc_path in documents.items():
        if not doc_path or not os.path.exists(doc_path):
            issues.append(f"{doc_type} file not found or missing")
            verified_docs[doc_type] = {'status': 'missing', 'confidence': 0}
            score -= 30
            continue

        # Attempt OCR extraction
        extracted_text = _extract_text(doc_path)
        doc_result = _verify_document(doc_type, extracted_text, full_name)
        verified_docs[doc_type] = doc_result

        if doc_result['status'] == 'invalid':
            issues.append(f"{doc_type}: {doc_result.get('reason', 'Verification failed')}")
            score -= 20
        elif doc_result['status'] == 'suspicious':
            issues.append(f"{doc_type}: {doc_result.get('reason', 'Suspicious content detected')}")
            score -= 10

    score = max(0, score)
    overall_status = 'verified' if score >= 70 and not any(
        v['status'] == 'missing' for v in verified_docs.values()
    ) else 'failed'

    return {
        'status': overall_status,
        'score': score,
        'verified_docs': verified_docs,
        'issues': issues,
        'agent': 'Document Verification Agent'
    }

def _extract_text(file_path):
    """Extract text from document using EasyOCR."""
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        results = reader.readtext(file_path, detail=0)
        return ' '.join(results).lower()
    except Exception:
        # Fallback: return filename-based mock text for non-image files
        return os.path.basename(file_path).lower()

def _verify_document(doc_type, text, applicant_name):
    """Rule-based document verification."""
    doc_type_lower = doc_type.lower()

    if 'aadhaar' in doc_type_lower:
        # Aadhaar: 12-digit number pattern
        has_number = bool(re.search(r'\d{4}\s?\d{4}\s?\d{4}', text))
        has_name = any(part in text for part in applicant_name.split() if len(part) > 2)
        if has_number:
            return {'status': 'verified', 'confidence': 90, 'doc_type': 'Aadhaar Card'}
        return {'status': 'suspicious', 'confidence': 50, 'doc_type': 'Aadhaar Card',
                'reason': 'Aadhaar number could not be read from the document. Please upload a clear image showing the full 12-digit Aadhaar number.'}

    elif 'pan' in doc_type_lower:
        # PAN: ABCDE1234F pattern
        has_pan = bool(re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', text.upper()))
        if has_pan:
            return {'status': 'verified', 'confidence': 92, 'doc_type': 'PAN Card'}
        return {'status': 'suspicious', 'confidence': 55, 'doc_type': 'PAN Card',
                'reason': 'PAN number pattern not detected'}

    elif 'income' in doc_type_lower or 'salary' in doc_type_lower:
        # Income proof: look for salary/income keywords
        keywords = ['salary', 'income', 'annual', 'monthly', 'employer', 'company', 'rupees', 'inr', '\u20b9']
        matches = sum(1 for kw in keywords if kw in text)
        if matches >= 2:
            return {'status': 'verified', 'confidence': 85, 'doc_type': 'Income Proof'}
        return {'status': 'suspicious', 'confidence': 45, 'doc_type': 'Income Proof',
                'reason': 'Income-related keywords not found'}

    elif 'passport' in doc_type_lower or 'photo' in doc_type_lower:
        # Passport photo: verify it's an image file
        ext = os.path.splitext(doc_type_lower)[1].lower()
        if any(e in doc_type_lower for e in ['jpg', 'jpeg', 'png']):
            return {'status': 'verified', 'confidence': 80, 'doc_type': 'Passport Photo'}
        return {'status': 'suspicious', 'confidence': 60, 'doc_type': 'Passport Photo',
                'reason': 'Please upload a JPG or PNG image'}

    # Generic document
    return {'status': 'verified', 'confidence': 70, 'doc_type': doc_type}
