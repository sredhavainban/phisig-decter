from . import phishing_url_service
from . import phishing_website_service

def _label_from_text(text: str):
    t = (text or '').lower()
    if 'phishing' in t:
        return 'phishing'
    if 'legitimate' in t or 'not phishing' in t or 'legitimate url' in t or 'legitimate website' in t:
        return 'legitimate'
    # fallback: look for numeric predictions
    if '1' in t and '0' not in t:
        return 'phishing'
    return 'unknown'

def ensemble_predict(url: str) -> dict:
    """Run both URL- and Website-based detectors and combine by majority.
    Returns dict: {url, url_pred, site_pred, combined, confidence}
    """
    url_pred_text = phishing_url_service.predict_phishing_url(url)
    site_pred_text = phishing_website_service.predict_phishing_website(url)

    lab1 = _label_from_text(url_pred_text)
    lab2 = _label_from_text(site_pred_text)

    votes = {'phishing': 0, 'legitimate': 0, 'unknown': 0}
    votes[lab1] = votes.get(lab1, 0) + 1
    votes[lab2] = votes.get(lab2, 0) + 1

    if votes['phishing'] > votes['legitimate']:
        combined = 'Phishing'
    elif votes['legitimate'] > votes['phishing']:
        combined = 'Legitimate'
    else:
        combined = 'Suspicious (mixed)'

    confidence = max(votes.values()) / 2.0  # fraction of models agreeing (0.0-1.0)

    return {
        'url': url,
        'url_pred': url_pred_text,
        'site_pred': site_pred_text,
        'combined': combined,
        'confidence': confidence
    }
