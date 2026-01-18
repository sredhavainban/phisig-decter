import os
import joblib
import importlib.util

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PATH = os.path.join(BASE, 'models', 'phishing_website', 'phishing_model.pkl')
FE_PATH = os.path.join(BASE, 'models', 'phishing_website', 'feature_extraction.py')

_model = None
if os.path.exists(MODEL_PATH):
    try:
        _model = joblib.load(MODEL_PATH)
    except Exception:
        _model = None

# load URLFeatureExtractor class from feature_extraction.py if available
_extractor_module = None
if os.path.exists(FE_PATH):
    spec = importlib.util.spec_from_file_location('fe_site', FE_PATH)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        _extractor_module = mod
    except Exception:
        _extractor_module = None

def _dict_to_ordered_list(d):
    # deterministic ordering: sort keys
    keys = sorted(d.keys())
    vals = [d[k] for k in keys]
    # coerce to floats where possible
    out = []
    for v in vals:
        try:
            out.append(float(v))
        except Exception:
            out.append(0.0)
    return out

def predict_phishing_website(features) -> str:
    # If features provided directly (list), use them
    vec = None
    if isinstance(features, (list, tuple)):
        try:
            vec = [float(x) for x in features]
        except Exception:
            vec = None

    # If a string is provided, treat it as a URL to extract features
    if isinstance(features, str) and _extractor_module and hasattr(_extractor_module, 'URLFeatureExtractor'):
        try:
            extractor_class = getattr(_extractor_module, 'URLFeatureExtractor')
            extractor = extractor_class(features)
            model_feats = extractor.extract_model_features()
            if isinstance(model_feats, dict):
                vec = _dict_to_ordered_list(model_feats)
            elif isinstance(model_feats, list):
                vec = [float(x) for x in model_feats]
            else:
                return f'Extractor returned unsupported type: {type(model_feats)}'
        except Exception as e:
            # fallback: simple lexical features similar to URL service
            try:
                vec = [float(x) for x in _lightweight_from_string(features)]
            except Exception:
                return f'Feature extraction error: {e}'

    if _model and vec is not None:
        try:
            pred = _model.predict([vec])
            return 'Phishing Website' if int(pred[0]) == 1 else 'Legitimate Website'
        except Exception as e:
            return f'Model prediction error: {e}'

    # If model missing, show extracted features if available
    if vec is not None:
        return 'Features extracted: ' + str(vec)
    return 'Model not found. Place phishing_model.pkl in models/phishing_website/ or provide features.'


def _lightweight_from_string(s: str):
    try:
        ss = str(s)
    except Exception:
        ss = ''
    return [len(ss), ss.count('.'), ss.count('-'), 1 if '@' in ss else 0]
