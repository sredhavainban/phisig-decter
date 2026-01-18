import os
import joblib
from sklearn.exceptions import NotFittedError

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PATH = os.path.join(BASE, 'models', 'spam', 'spam_best_model.pkl')

_spam_model = None
if os.path.exists(MODEL_PATH):
    try:
        _spam_model = joblib.load(MODEL_PATH)
    except Exception:
        _spam_model = None

def predict_spam(text: str) -> dict:
    """Return structured spam prediction: {label, score, reasons, raw}.

    - label: 'spam'|'not_spam'|'unknown'
    - score: float 0..1 when available (heuristic or model probability)
    - reasons: list of strings explaining heuristic triggers
    - raw: original input
    """
    # default empty result
    res = {'label': 'unknown', 'score': None, 'reasons': [], 'raw': text}

    # If model present, try to use it
    if _spam_model:
        try:
            if hasattr(_spam_model, 'predict_proba'):
                prob = _spam_model.predict_proba([text])
                score = float(prob[0][1])
                res['score'] = score
                res['label'] = 'spam' if score >= 0.5 else 'not_spam'
                return res
            else:
                pred = _spam_model.predict([text])
                res['label'] = 'spam' if int(pred[0]) == 1 else 'not_spam'
                res['score'] = 1.0 if res['label'] == 'spam' else 0.0
                return res
        except NotFittedError:
            # fall through to rule-based
            pass
        except Exception:
            # fall through to rule-based
            pass

    # No usable model — use rule-based heuristic and return explanations
    is_spam = _rule_based_spam(text)
    # construct simple score and reasons
    reasons = []
    s = (text or '').lower()
    spam_terms = ['win', 'won', 'congrat', 'free', 'prize', 'click here', 'unsubscribe', 'money', 'credit card']
    hits = [t for t in spam_terms if t in s]
    if hits:
        reasons.append('Contains spammy terms: ' + ', '.join(hits))
    if any(ch.isupper() for ch in text or '') and len(text or '') < 200:
        reasons.append('Excessive uppercase text')
    if len(text or '') < 20 and is_spam:
        reasons.append('Very short message with spam indicators')

    score = 0.9 if is_spam else 0.05
    res['label'] = 'spam' if is_spam else 'not_spam'
    res['score'] = score
    res['reasons'] = reasons
    return res


def _rule_based_spam(text: str) -> bool:
    if not text:
        return False
    s = text.lower()
    spam_terms = ['win', 'won', 'congrat', 'free', 'prize', 'click here', 'unsubscribe', 'money', 'credit card']
    score = 0
    for t in spam_terms:
        if t in s:
            score += 1
    return score >= 1
