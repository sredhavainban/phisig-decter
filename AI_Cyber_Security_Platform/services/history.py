import sqlite3
import os
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE, 'predictions.db')

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _init():
    if not os.path.exists(DB_PATH):
        conn = _get_conn()
        c = conn.cursor()
        c.execute('''CREATE TABLE predictions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      service TEXT,
                      input TEXT,
                      result TEXT,
                      created_at TEXT)''')
        conn.commit()
        conn.close()

_init()

def save_prediction(service, input_text, result):
    conn = _get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO predictions (service, input, result, created_at) VALUES (?,?,?,?)',
              (service, input_text, result, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_stats():
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM predictions")
    total = c.fetchone()['total']
    c.execute("SELECT COUNT(*) as spam_detected FROM predictions WHERE service='spam' AND result LIKE '%Spam%'")
    spam_detected = c.fetchone()['spam_detected']
    c.execute("SELECT COUNT(*) as url_checked FROM predictions WHERE service='phishing_url'")
    url_checked = c.fetchone()['url_checked']
    conn.close()
    return {'total': total, 'spam_detected': spam_detected, 'url_checked': url_checked}

def get_last_prediction():
    conn = _get_conn()
    c = conn.cursor()
    c.execute('SELECT service, input, result, created_at FROM predictions ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_qr_quishing_stats():
    """Aggregate QR quishing stats from the predictions table.

    Returns dict with keys: qr_scans, quishing_detected, redirect_traversals
    """
    conn = _get_conn()
    c = conn.cursor()
    # We store QR scans using service='quishing'
    c.execute("SELECT result FROM predictions WHERE service='quishing'")
    rows = c.fetchall()
    conn.close()

    total_scans = 0
    quishing_detected = 0
    total_traversals = 0
    import json
    for r in rows:
        total_scans += 1
        res_text = r['result'] if isinstance(r, dict) and 'result' in r else r[0] if isinstance(r, tuple) else r['result'] if 'result' in r else r
        try:
            parsed = json.loads(res_text)
        except Exception:
            # result may already be a stringified simple value; skip
            parsed = {}
        # risk_level may be at top-level or nested; try common keys
        risk = parsed.get('risk_level') if isinstance(parsed, dict) else None
        if not risk:
            # fallback: try to read from parsed['result'] if nested
            try:
                nested = parsed.get('result') if isinstance(parsed, dict) else None
                if isinstance(nested, dict):
                    risk = nested.get('risk_level')
            except Exception:
                risk = None
        redirect_count = 0
        try:
            redirect_count = int(parsed.get('redirect_count', 0) or 0)
        except Exception:
            redirect_count = 0

        if risk and (('MEDIUM' in risk) or ('HIGH' in risk) or ('CRITICAL' in risk) or (risk not in ('LOW', 'UNKNOWN'))):
            quishing_detected += 1
        total_traversals += redirect_count

    return {
        'qr_scans': total_scans,
        'quishing_detected': quishing_detected,
        'redirect_traversals': total_traversals
    }
