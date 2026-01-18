import os
import importlib.util
import joblib
import re
try:
    # prefer package import if available
    from models.phishing_url.feature_extraction import *
    _feature_extractor_pkg = True
except Exception:
    _feature_extractor_pkg = False

# This service expects:
# - feature_extraction.py with a `main(url)` function that returns a list of features
# - optional model at models/phishing_url/phishing_url_model.pkl

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FE_PATH = os.path.join(BASE, 'models', 'phishing_url', 'feature_extraction.py')
MODEL_PATH = os.path.join(BASE, 'models', 'phishing_url', 'phishing_url_model.pkl')

_feature_extractor = None
if not _feature_extractor_pkg and os.path.exists(FE_PATH):
    spec = importlib.util.spec_from_file_location('fe', FE_PATH)
    fe = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(fe)
        _feature_extractor = fe
    except Exception:
        _feature_extractor = None

_model = None
if os.path.exists(MODEL_PATH):
    try:
        _model = joblib.load(MODEL_PATH)
    except Exception:
        _model = None

def _coerce_list_to_floats(lst):
    out = []
    for v in lst:
        if v in (None, '?', ''):
            out.append(0.0)
            continue
        if isinstance(v, str) and v.lower() in ('true', 'false'):
            out.append(1.0 if v.lower() == 'true' else 0.0)
            continue
        try:
            out.append(float(v))
        except Exception:
            out.append(0.0)
    return out


def _lightweight_extract(url: str):
    """Return a small list of lexical features suitable as a fallback.
    Features: length, dot_count, hyphen_count, has_at, has_ip, has_https
    """
    try:
        s = str(url)
    except Exception:
        s = ''
    length = len(s)
    dot_count = s.count('.')
    hyphen_count = s.count('-')
    has_at = 1 if '@' in s else 0
    has_ip = 1 if re.search(r'\d+\.\d+\.\d+\.\d+', s) else 0
    has_https = 1 if s.startswith('https') or s.startswith('https://') else 0
    return [length, dot_count, hyphen_count, has_at, int(has_ip), int(has_https)]

def _call_extractor(url: str):
    # try common function names in extractor modules
    # prefer package module
    if _feature_extractor_pkg:
        pkg = importlib.import_module('models.phishing_url.feature_extraction')
        for fname in ('main', 'extract_features', 'extract_features_from_url', 'extract'):
            if hasattr(pkg, fname):
                return getattr(pkg, fname)(url)
    if not _feature_extractor:
        raise FileNotFoundError('Feature extractor not found')
    for fname in ('main', 'extract_features', 'extract_features_from_url', 'extract'):
        if hasattr(_feature_extractor, fname):
            func = getattr(_feature_extractor, fname)
            return func(url)
    # fallback: try functions that start with 'extract' or 'get'
    for name in dir(_feature_extractor):
        if name.lower().startswith('extract') or name.lower().startswith('get'):
            attr = getattr(_feature_extractor, name)
            if callable(attr):
                try:
                    return attr(url)
                except Exception:
                    continue
    raise AttributeError('No suitable extractor function found in feature_extraction.py')


def _heuristic_score_url(url: str, features: list):
    """Lightweight heuristic that returns (score, reasons).

    Reasons is a list of short strings explaining which checks contributed.
    """
    s = str(url).strip().lower()
    score = 0.0
    weight = 0.0
    reasons = []

    def add(w, reason=None, v=1.0):
        nonlocal score, weight
        score += w * v
        weight += w
        if reason:
            reasons.append(reason)

    # IP address in URL
    if re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", s):
        add(3.0, 'IP address in host')

    # @ symbol often used in phishing
    if '@' in s:
        add(2.5, "'@' symbol in URL")

    # double dots or many dots
    if '..' in s or re.search(r"\.{3,}", s):
        add(2.0, 'Consecutive dots found')

    # long URL
    if len(s) > 75:
        add(1.5, 'Long URL')

    # host analysis
    host = s
    try:
        host = re.sub(r'^https?://', '', host)
        host = host.split('/')[0]
    except Exception:
        pass
    dots = host.count('.')
    if dots >= 4:
        add(1.5, 'Many subdomains')
    elif dots >= 2:
        add(0.5, f'{dots} dots in host')

    # suspicious tokens
    for token in ('login', 'signin', 'verify', 'confirm', 'account', 'secure', 'bank', 'update'):
        if token in s:
            add(1.0, f"Suspicious token: {token}")

    # hyphens
    hyph = host.count('-')
    if hyph >= 3:
        add(1.0, 'Many hyphens in host')
    elif hyph > 0:
        add(0.2, f'{hyph} hyphens')

    # feature-derived heuristics (if features provided)
    try:
        if features and len(features) > 0:
            flen = float(features[0])
            if flen > 100:
                add(0.8, 'Very long URL (from features)')
    except Exception:
        pass

    if weight <= 0:
        return 0.0, []
    val = score / (weight + 1e-9)
    val = max(0.0, min(1.0, val))
    return val, reasons


def predict_phishing_url(url: str) -> dict:
    """Return a structured dict: {label, score, features}
    - label: 'phishing'|'legitimate'|'unknown'
    - score: probability-like float 0..1 when available
    - features: numeric feature list
    """
    try:
        feats = _call_extractor(url)
    except FileNotFoundError:
        feats = _lightweight_extract(url)
    except Exception:
        feats = _lightweight_extract(url)

    numeric = _coerce_list_to_floats(feats)
    out = {'label': 'unknown', 'score': None, 'features': numeric}
    if _model:
        try:
            # prefer probability if available
            if hasattr(_model, 'predict_proba'):
                prob = _model.predict_proba([numeric])
                # assume binary: class 1 -> phishing
                score = float(prob[0][1])
                pred = 1 if score >= 0.5 else 0
                out['score'] = score
                out['label'] = 'phishing' if pred == 1 else 'legitimate'
            else:
                pred = _model.predict([numeric])
                out['label'] = 'phishing' if int(pred[0]) == 1 else 'legitimate'
        except Exception:
            out['label'] = 'error'
            out['score'] = None
    else:
        # No trained model available — use a heuristic scorer to derive label, score, and reasons
        score, reasons = _heuristic_score_url(url, numeric)
        out['score'] = score
        out['label'] = 'phishing' if score >= 0.5 else 'legitimate'
        out['reasons'] = reasons
    return out
