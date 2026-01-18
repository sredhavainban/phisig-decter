from .ocr_utils import extract_text
from .phishing_rules import is_phishing
import re


def _highlight_text(text: str, matches: list) -> str:
    """Return HTML with matched phrases wrapped in <mark> tags.

    Performs case-insensitive replacement and prefers longer matches first
    to avoid partial overlapping replacements.
    """
    if not text or not matches:
        return text or ''
    out = text
    # sort by length descending to avoid shorter matches eating parts of longer ones
    uniq = sorted(set(matches), key=lambda x: -len(x))
    for kw in uniq:
        try:
            pattern = re.compile(re.escape(kw), flags=re.IGNORECASE)
            out = pattern.sub(lambda m: f"<span class='phish'>{m.group(0)}</span>", out)
        except Exception:
            continue
    return out


def predict_webpage(image_path: str, threshold: int = 3) -> dict:
    """Predict whether a webpage screenshot is phishing.

    Simplified predictor: OCR -> keyword rules -> produce structured dict.
    Returns dict: {label, score, matches, extracted_text, highlighted_text, image_path}
    """
    text = extract_text(image_path)
    phishing, score, matches = is_phishing(text, threshold=threshold)
    # Classification levels
    if score >= threshold:
        label = 'PHISHING WEBSITE'
        badge = 'danger'
    elif score == max(0, threshold - 1):
        label = 'SUSPICIOUS WEBSITE'
        badge = 'warning'
    else:
        label = 'LEGITIMATE WEBSITE'
        badge = 'success'

    # Simple confidence: scale score -> percent (user suggested simple mapping)
    try:
        confidence = min(100, int(score * 30))
    except Exception:
        confidence = 0

    highlighted = _highlight_text(text, matches)
    return {
        'label': label,
        'badge': badge,
        'score': float(score) if score is not None else 0.0,
        'matches': matches,
        'extracted_text': text,
        'highlighted_text': highlighted,
        'confidence': confidence,
        'image_path': image_path,
    }
