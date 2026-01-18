import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE, 'predictions.db')

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _init():
    conn = _get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT
    )''')
    conn.commit()
    # ensure at least one admin user exists
    c.execute('SELECT COUNT(*) as cnt FROM users')
    if c.fetchone()['cnt'] == 0:
        pw = generate_password_hash('admin')
        c.execute('INSERT INTO users (username, password_hash, created_at) VALUES (?,?,?)', ('admin', pw, datetime.utcnow().isoformat()))
        conn.commit()
    conn.close()

_init()

def create_user(username, password):
    conn = _get_conn()
    c = conn.cursor()
    ph = generate_password_hash(password)
    try:
        c.execute('INSERT INTO users (username, password_hash, created_at) VALUES (?,?,?)', (username, ph, datetime.utcnow().isoformat()))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = _get_conn()
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE username=?', (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    return check_password_hash(row['password_hash'], password)
