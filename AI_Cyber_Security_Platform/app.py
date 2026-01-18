from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import send_file
from services.spam_service import predict_spam
from services.phishing_url_service import predict_phishing_url
from services.phishing_website_service import predict_phishing_website
from services import history
from services import auth
from services import ensemble
from flask import session
import os
from werkzeug.utils import secure_filename

# lazy import of our new module
try:
    from models.webpage_phishing import predict_webpage
    # import OCR helper and rules so we can ensure OCR output flows through the route
    try:
        from models.webpage_phishing import ocr_utils
    except Exception:
        ocr_utils = None
except Exception:
    predict_webpage = None

# QR Quishing detector (lazy import so app still starts without opencv/requests)
try:
    from services.quishing_detector import analyze_qr_quishing
except Exception:
    analyze_qr_quishing = None

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'change-me-to-a-secure-random-value'
# configure upload folder inside static so Flask can serve uploaded images
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# BASE: use repository working directory for any file writes so paths are Linux-friendly
BASE = os.getcwd()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/spam')
def spam_page():
    return render_template('spam.html')

@app.route('/phishing-url')
def phishing_url_page():
    return render_template('phishing_url.html')

@app.route('/phishing-website')
def phishing_website_page():
    return render_template('phishing_website.html')


@app.route('/webpage-phishing', methods=['GET', 'POST'])
def webpage_phishing_page():
    # This route handles the Webpage Screenshot Phishing Detection UI.
    # We standardize all predictor outputs into a stable `result` dict with keys:
    #  - label (string), score (float), confidence (float), matches (list),
    #  - extracted_text (string), highlighted_text (html string), image_path (static/uploads/...)
    # Defensive behavior: if upload is missing or OCR/predictor fails we still return
    # a structured `result` object (so the template can render safely without errors).
    result = None
    if request.method == 'POST':
        f = request.files.get('image')
        # allow adjustable threshold from the form (default 3)
        try:
            threshold = int(request.form.get('threshold', 3))
        except Exception:
            threshold = 3
        if f and f.filename:
            filename = secure_filename(f.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(save_path)
            # Run OCR directly and use a rule-based fallback detector to guarantee the pipeline
            try:
                ocr_text = ''
                # 1) Ensure OCR is called on the saved image and print the text for debugging
                if ocr_utils and hasattr(ocr_utils, 'extract_text_from_image'):
                    try:
                        ocr_text = ocr_utils.extract_text_from_image(save_path) or ''
                        print('OCR_EXTRACTED_TEXT:', repr(ocr_text))
                        print('OCR_LENGTH=', len(ocr_text))
                    except Exception as _e:
                        print('OCR helper error:', _e)
                        ocr_text = ''
                else:
                    # If OCR helper isn't available, try using the predictor (best-effort)
                    try:
                        raw_try = predict_webpage(save_path, threshold=threshold) if predict_webpage else {}
                        ocr_text = (raw_try.get('extracted_text') or raw_try.get('text') or '')
                        print('OCR (from predictor) length=', len(ocr_text))
                    except Exception:
                        ocr_text = ''

                # 2) Normalize extracted text for detection
                normalized = (ocr_text or '').strip().lower()

                # 3) Rule-based fallback detector (guaranteed to run):
                indicators = [
                    'urgent', 'verify', 'account', 'login', 'password', 'compromised', 'unusual activity'
                ]
                matches = []
                for kw in indicators:
                    try:
                        if kw in normalized:
                            matches.append(kw)
                    except Exception:
                        continue

                score = len(matches)
                total = len(indicators)
                confidence = (float(score) / float(total) * 100.0) if total > 0 else 0.0

                # 4) Determine label from score vs threshold
                if score >= int(threshold):
                    label = 'PHISHING WEBSITE'
                else:
                    label = 'LEGITIMATE WEBSITE'

                # 5) Defensive handling: if OCR produced no readable text, set friendly message
                display_text = ocr_text if (ocr_text and ocr_text.strip()) else 'No readable text detected from screenshot.'

                result = {
                    'label': label,
                    'score': float(score),
                    'confidence': float(min(100.0, confidence)),
                    'matches': matches,
                    'extracted_text': display_text,
                    'highlighted_text': display_text,
                    'image_path': os.path.join('uploads', filename).replace('\\', '/'),
                    'has_prediction': True
                }

                # Persist debug result
                try:
                    import json as _json
                    with open(os.path.join(BASE if 'BASE' in globals() else '.', 'webpage_last_result.json'), 'w', encoding='utf-8') as fh:
                        _json.dump(result, fh, ensure_ascii=False, indent=2)
                except Exception:
                    pass
                print('WEBPAGE_PREDICTION_RESULT:', result)

            except Exception as e:
                print('Webpage detection pipeline error:', e)
                result = {'label': 'LEGITIMATE WEBSITE', 'score': 0.0, 'confidence': 0.0, 'matches': [], 'extracted_text': f'Internal error: {str(e)}', 'highlighted_text': '', 'image_path': os.path.join('uploads', filename).replace('\\', '/'), 'has_prediction': True}
            # save history
            try:
                import json as _json
                history.save_prediction('webpage_phishing', filename, _json.dumps(result))
            except Exception:
                history.save_prediction('webpage_phishing', filename, str(result))
        else:
            # Defensive: no file uploaded or empty filename
            # Use LEGITIMATE fallback and mark as a prediction (has_prediction=True)
            result = {
                'label': 'LEGITIMATE WEBSITE',
                'score': 0.0,
                'confidence': 0.0,
                'matches': [],
                'extracted_text': 'No file uploaded',
                'highlighted_text': '',
                'image_path': '',
                'has_prediction': True
            }
        # If OCR returned empty or whitespace-only text, normalize to LEGITIMATE with friendly message
        try:
            etxt = (result.get('extracted_text') or '').strip()
            if request.method == 'POST' and (etxt == '' or etxt.isspace()):
                result['label'] = 'LEGITIMATE WEBSITE'
                result['score'] = 0.0
                result['confidence'] = 0.0
                result['matches'] = []
                result['extracted_text'] = 'No readable text detected from screenshot.'
                result['highlighted_text'] = ''
        except Exception:
            pass
    # If no result set (GET request), return a minimal result indicating no prediction yet
    if not result:
        result = {'has_prediction': False}

    # pass threshold so the form retains its value
    return render_template('webpage_phishing.html', result=result, threshold=threshold if request.method=='POST' else 3)


@app.route('/logo.png')
def serve_root_logo():
    """Serve a workspace-level logo.png if present at repository root.

    This lets users drop a `logo.png` in the repo root and have the UI show it
    without requiring them to move files into the `/static` folder.
    """
    root_logo = os.path.join(os.getcwd(), 'logo.png')
    if os.path.exists(root_logo):
        try:
            return send_file(root_logo, mimetype='image/png')
        except Exception:
            pass
    # fallback 404 so browser doesn't attempt to use a missing image
    return ('', 404)

@app.route('/api/spam', methods=['POST'])
def spam_api():
    data = request.get_json() or {}
    text = data.get('text', '')
    result = predict_spam(text)
    # store structured result (stringify) in history
    try:
        import json as _json
        history.save_prediction('spam', text, _json.dumps(result))
    except Exception:
        history.save_prediction('spam', text, str(result))
    return jsonify(result)

@app.route('/api/phishing-url', methods=['POST'])
def phishing_url_api():
    data = request.get_json() or {}
    url = data.get('url', '')
    result = predict_phishing_url(url)
    # store stringified result in history
    try:
        import json as _json
        history.save_prediction('phishing_url', url, _json.dumps(result))
    except Exception:
        history.save_prediction('phishing_url', url, str(result))
    return jsonify(result)

@app.route('/api/phishing-website', methods=['POST'])
def phishing_website_api():
    data = request.get_json() or {}
    features = data.get('features')
    result = predict_phishing_website(features)
    history.save_prediction('phishing_website', str(features), result)
    return jsonify({'result': result})


@app.route('/dashboard')
def dashboard():
    # dashboard is public now (login removed)
    stats = history.get_stats()
    last = history.get_last_prediction()
    # QR quishing summary
    try:
        qr_stats = history.get_qr_quishing_stats()
    except Exception:
        qr_stats = {'qr_scans': 0, 'quishing_detected': 0, 'redirect_traversals': 0}
    return render_template('home.html', stats=stats, last=last, qr_stats=qr_stats)


@app.route('/ensemble', methods=['POST'])
def ensemble_api():
    data = request.get_json() or {}
    url = data.get('url', '')
    res = ensemble.ensemble_predict(url)
    history.save_prediction('ensemble', url, res.get('combined'))
    return jsonify(res)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login page removed from project.
    return redirect(url_for('dashboard'))


@app.route('/signup', methods=['GET'])
def signup():
    # Signup page removed from project.
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    # Clear server session (if any) and return to dashboard.
    session.pop('username', None)
    return redirect(url_for('dashboard'))


def _require_login(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*a, **kw):
        if not session.get('username'):
            return redirect(url_for('login'))
        return func(*a, **kw)
    return wrapper


@app.route('/history')
def history_page():
    # history is public now (login removed)
    conn = history._get_conn()
    c = conn.cursor()
    c.execute('SELECT id, service, input, result, created_at FROM predictions ORDER BY id DESC LIMIT 200')
    rows = c.fetchall()
    conn.close()
    return render_template('history.html', rows=rows)


@app.route('/qr-quishing', methods=['GET', 'POST'])
def qr_quishing_page():
    # Simple UI to upload a QR image and analyze redirect chain using the quishing detector
    result = None
    if request.method == 'POST':
        f = request.files.get('image')
        if f and f.filename:
            filename = secure_filename(f.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(save_path)
            # If detector is available, run it; otherwise return a friendly error
            try:
                if analyze_qr_quishing:
                    det = analyze_qr_quishing(save_path)
                else:
                    det = {'error': 'QR detector not available (missing dependencies)'}
            except Exception as e:
                det = {'error': f'Internal detector error: {str(e)}'}

            # ensure result contains image_path for template preview
            det['image_path'] = os.path.join('uploads', filename).replace('\\', '/')
            result = det
            # Save to history table for auditing
            try:
                import json as _json
                history.save_prediction('quishing', filename, _json.dumps(result))
            except Exception:
                history.save_prediction('quishing', filename, str(result))
        else:
            result = {'error': 'No file uploaded', 'image_path': ''}

    if not result:
        result = {'has_prediction': False}
    return render_template('quishing.html', result=result)

if __name__ == '__main__':
    # Run on 0.0.0.0:7860 for Hugging Face Spaces compatibility (CPU-only)
    # Do NOT enable debug mode in production
    app.run(host='0.0.0.0', port=7860)
