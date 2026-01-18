import json
import sys
from pathlib import Path
# ensure repo root is on sys.path so `services` and `models` packages import correctly
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
	sys.path.insert(0, repo_root)

from services.brand_consistency import analyze_brand_consistency

url = "http://secure-paypal-login.example.net/login"
html = "PayPal - Account Login"
ocr = "Welcome to PayPal. Please verify your account."

res = analyze_brand_consistency(url, html, ocr)
print(json.dumps(res, indent=2))
