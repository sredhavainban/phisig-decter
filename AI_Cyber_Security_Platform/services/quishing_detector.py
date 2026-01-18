"""
QR Quishing Detection using Redirection Chain Analysis

Provides a single callable function:

  analyze_qr_quishing(image_path: str) -> dict

Functionality:
- Decode a QR code from an image using OpenCV's QRCodeDetector
- Extract the embedded URL
- Follow the HTTP redirection chain (requests)
- Classify risk by number of redirects
- Return structured JSON with explanation

This module is independent and does not modify other services.
Designed to be lightweight and CPU-only.
"""
from typing import List, Dict, Any
import os
import urllib.parse
import socket

try:
    import cv2
except Exception as e:
    cv2 = None

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
except Exception:
    pyzbar_decode = None

import requests


def _safe_decode_qr(image_path: str) -> str:
    """Attempt to decode a QR code using OpenCV QRCodeDetector.

    Returns the decoded string (usually a URL) or empty string on failure.
    """
    # robust pipeline: prefer pyzbar; preprocess with grayscale, binarization, and resize fallbacks
    if cv2 is None:
        return ''
    if not os.path.exists(image_path):
        return ''
    try:
        # Load in color first for pyzbar (it accepts numpy images)
        img_color = cv2.imread(image_path)
        if img_color is None:
            return ''

        # QUICK SIZE CHECK: if very small, upscale early
        h0, w0 = img_color.shape[:2]
        if h0 < 200 or w0 < 200:
            scale = max(200 / max(h0, w0), 1.0)
            new_w = int(w0 * scale)
            new_h = int(h0 * scale)
            img_color = cv2.resize(img_color, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

        # 1) Try pyzbar first on color image
        if pyzbar_decode is not None:
            try:
                decoded = pyzbar_decode(img_color)
                if decoded:
                    return decoded[0].data.decode('utf-8').strip()
            except Exception:
                pass

        # Convert to grayscale for OpenCV processing
        gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

        # 2) Try OpenCV detector on gray
        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(gray)
        if data:
            return data.strip()

        # 3) Preprocess: Otsu binarization then try pyzbar + OpenCV
        try:
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        except Exception:
            binary = None

        if binary is not None:
            # pyzbar on binary
            if pyzbar_decode is not None:
                try:
                    decoded = pyzbar_decode(binary)
                    if decoded:
                        return decoded[0].data.decode('utf-8').strip()
                except Exception:
                    pass

            # OpenCV on binary
            data, points, _ = detector.detectAndDecode(binary)
            if data:
                return data.strip()

        # 4) Resize (zoom) fallback: try larger scales
        try_scales = [2.0, 3.0]
        for s in try_scales:
            try:
                resized = cv2.resize(binary if binary is not None else gray, (0, 0), fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
                if pyzbar_decode is not None:
                    try:
                        decoded = pyzbar_decode(resized)
                        if decoded:
                            return decoded[0].data.decode('utf-8').strip()
                    except Exception:
                        pass
                data, points, _ = detector.detectAndDecode(resized)
                if data:
                    return data.strip()
            except Exception:
                continue

    except Exception:
        return ''
    return ''


def _follow_redirects(url: str, timeout: int = 10, max_redirects: int = 20) -> Dict[str, Any]:
    """Follow HTTP redirections for a URL and return chain info.

    Uses `requests` with `allow_redirects=True` and captures `response.history`.
    Returns dict with keys: redirect_chain (list of URLs), redirect_count (int), final_url (str)
    """
    session = requests.Session()
    session.max_redirects = max_redirects
    headers = {
        'User-Agent': 'PhishGuard-Quishing-Detector/1.0 (+https://example.local)'
    }
    try:
        # Use GET with stream to avoid downloading large bodies unnecessarily
        resp = session.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
        chain = [r.url for r in resp.history] if resp.history else []
        final = resp.url
        # include final in chain return (but keep history separate for count)
        redirect_count = len(chain)
        full_chain = chain + [final]
        # close streamed response
        try:
            resp.close()
        except Exception:
            pass
        return {
            'redirect_chain': full_chain,
            'redirect_count': redirect_count,
            'final_url': final,
        }
    except requests.exceptions.TooManyRedirects:
        return {
            'redirect_chain': [],
            'redirect_count': max_redirects,
            'final_url': url,
        }
    except Exception:
        return {
            'redirect_chain': [],
            'redirect_count': 0,
            'final_url': url,
        }


def _classify_risk(redirect_count: int) -> str:
    if redirect_count <= 1:
        return 'LOW'
    if 2 <= redirect_count <= 3:
        return 'MEDIUM'
    return 'HIGH'


def _explain(decoded_url: str, redirect_chain: List[str], redirect_count: int, final_url: str) -> str:
    reasons = []
    if not decoded_url:
        return 'No QR code could be decoded from the image.'
    reasons.append(f'QR decoded to: {decoded_url}')
    if redirect_count == 0:
        reasons.append('The URL does not perform redirections (direct link).')
    else:
        reasons.append(f'{redirect_count} intermediate redirect(s) were observed.')
        # Check if final domain differs from start domain
        try:
            s_domain = urllib.parse.urlparse(decoded_url).hostname or ''
            f_domain = urllib.parse.urlparse(final_url).hostname or ''
            if s_domain and f_domain and s_domain.lower() != f_domain.lower():
                reasons.append(f'Final host ({f_domain}) differs from initial host ({s_domain}), this can indicate URL masking.')
        except Exception:
            pass

    # brief security note
    if redirect_count >= 4:
        reasons.append('Multiple redirects may be used to obfuscate the final landing page and evade detection—treat as HIGH risk.')
    elif redirect_count >= 2:
        reasons.append('A moderate number of redirects found; final landing page should be inspected before clicking.')
    else:
        reasons.append('Few or no redirects found; likely lower risk but always inspect the final destination.')

    return ' '.join(reasons)


def _final_domain(url: str) -> str:
    try:
        return (urllib.parse.urlparse(url).hostname or '')
    except Exception:
        return ''


def analyze_qr_risk(scanned_url: str) -> Dict[str, Any]:
    """Unshorten and analyze the final URL for suspicious patterns.

    Returns a dict with keys: final_url, risk_level, warnings
    """
    results = {
        'final_url': scanned_url,
        'risk_level': 'LOW',
        'warnings': []
    }

    # STEP 1: Unshorten (follow redirects) using HEAD
    try:
        response = requests.head(scanned_url, allow_redirects=True, timeout=5)
        results['final_url'] = response.url
        if response.history:
            results['warnings'].append(f"Redirected {len(response.history)} times")
    except Exception:
        results['warnings'].append('URL is unreachable (Potential Block)')

    # STEP 2: Analyze destination
    final_url_lower = results['final_url'].lower()
    parsed_domain = urllib.parse.urlparse(results['final_url']).netloc

    bad_keywords = ["login", "verify", "secure", "account", "update", "bank", "confirm"]
    safe_domains = ["google.com", "microsoft.com", "paypal.com", "youtube.com"]

    keyword_hits = [word for word in bad_keywords if word in final_url_lower]
    if keyword_hits and parsed_domain not in safe_domains:
        results['warnings'].append(f"Suspicious keywords found: {keyword_hits}")

    # Check B: IP address usage
    if parsed_domain.replace('.', '').isnumeric():
        results['warnings'].append('Destination is a raw IP address (High Risk)')

    # STEP 3: Verdict
    if 'IP address' in str(results['warnings']) or keyword_hits:
        results['risk_level'] = 'CRITICAL (PHISHING)'
    elif len(results['warnings']) >= 1:
        results['risk_level'] = 'MODERATE (SUSPICIOUS)'

    return results


def analyze_qr_quishing(image_path: str) -> Dict[str, Any]:
    """Main public function.

    Parameters
    - image_path: path to an image file containing a QR code

    Returns a dict with the structure:
    {
      "decoded_url": str or None,
      "redirect_chain": [str,...],
      "redirect_count": int,
      "final_url": str,
      "risk_level": "LOW|MEDIUM|HIGH|UNKNOWN",
      "security_explanation": str
    }
    """
    decoded = _safe_decode_qr(image_path)
    if not decoded:
        return {
            'decoded_url': None,
            'redirect_chain': [],
            'redirect_count': 0,
            'final_url': None,
            'final_domain': None,
            'risk_level': 'UNKNOWN',
            'reason_for_risk': 'Unable to decode QR reliably',
            'user_warning': 'QR image detected, but decoding failed due to image quality or scaling. Try uploading the original QR image or a higher-resolution version.',
            'security_explanation': 'QR image detected, but decoding failed due to image quality or scaling. Try uploading the original QR image or a higher-resolution version.'
        }

    # Normalize URL: if QR contains a mailto or text, handle conservatively
    parsed = urllib.parse.urlparse(decoded)
    if not parsed.scheme:
        # assume http if no scheme present
        decoded = 'http://' + decoded

    # Follow redirects (quick analysis) then perform deeper URL risk analysis
    follow = _follow_redirects(decoded)
    redirect_chain = follow.get('redirect_chain', [])
    redirect_count = follow.get('redirect_count', 0)
    final_url = follow.get('final_url', decoded)

    # Auditor-friendly explanation from redirect observation
    explanation_text = _explain(decoded, redirect_chain[:-1] if len(redirect_chain)>0 else [], redirect_count, final_url)

    # URL risk analysis (unshorten + heuristics)
    try:
        url_analysis = analyze_qr_risk(decoded)
    except Exception:
        url_analysis = None

    # Merge results: prefer URL analysis when available
    if url_analysis:
        final_url = url_analysis.get('final_url') or final_url
        redirect_count = url_analysis.get('redirect_count', redirect_count)
        risk_level = url_analysis.get('risk_level', 'LOW')
        warnings = url_analysis.get('warnings', [])
    else:
        # Fallback to simple classifier
        risk_level = _classify_risk(redirect_count)
        warnings = []

    final_domain = _final_domain(final_url) if final_url else ''

    # Build user-friendly warning
    user_warning = ''
    if isinstance(risk_level, str) and 'CRITICAL' in risk_level:
        user_warning = 'HIGH RISK — Do not visit the final URL. It may be malicious.'
    elif isinstance(risk_level, str) and ('MODERATE' in risk_level or 'SUSPICIOUS' in risk_level):
        user_warning = 'MEDIUM RISK — Inspect the final URL before visiting.'
    elif risk_level == 'HIGH':
        user_warning = 'HIGH RISK — Do not visit the final URL. It may be malicious.'
    elif risk_level == 'MEDIUM':
        user_warning = 'MEDIUM RISK — Inspect the final URL before visiting.'
    else:
        user_warning = 'LOW RISK — Exercise normal caution before visiting.'

    return {
        'decoded_url': decoded,
        'redirect_chain': redirect_chain,
        'redirect_count': redirect_count,
        'final_url': final_url,
        'final_domain': final_domain,
        'risk_level': risk_level,
        'warnings': warnings,
        'user_warning': user_warning,
        'security_explanation': explanation_text,
    }


if __name__ == '__main__':
    # Simple CLI test
    import json, sys
    if len(sys.argv) < 2:
        print('Usage: python quishing_detector.py path/to/qr.png')
        sys.exit(1)
    res = analyze_qr_quishing(sys.argv[1])
    print(json.dumps(res, indent=2))
