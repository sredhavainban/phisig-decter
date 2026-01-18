"""
models/brand_consistency/utils.py

Utility helpers for the Brand Consistency Analyzer.

Functions:
 - extract_domain_token(url): heuristic SLD extraction
 - normalize_tokens(text): tokenize, normalize and deduplicate tokens
 - best_match_ratio(token, token_list): best fuzzy match ratio between token and list

All functions use only Python stdlib for portability on Hugging Face.
"""
import re
from urllib.parse import urlparse
import difflib
from typing import List, Optional


def extract_domain_token(url: str) -> str:
    """Heuristically extract a primary domain token from a URL.

    Example: secure-paypal-login.example.com -> paypal
    This is a heuristic: it picks the second-level domain when possible.
    """
    try:
        parsed = urlparse(url if url else "")
        host = parsed.netloc or parsed.path  # support plain host strings
        host = host.lower().strip()
        # remove port
        host = host.split(":")[0]
        parts = [p for p in host.split('.') if p]
        if not parts:
            return ""
        if len(parts) == 1:
            token = parts[0]
        else:
            # take the second-level domain (heuristic)
            token = parts[-2]
        # further split on dashes/underscores and pick middle token if hyphenated
        subtokens = re.split(r'[-_]', token)
        # choose the longest subtoken (likely brand)
        token = max(subtokens, key=len) if subtokens else token
        token = re.sub(r'[^a-z0-9]', '', token)
        return token
    except Exception:
        return ""


def normalize_tokens(text: str) -> List[str]:
    """Tokenize and normalize textual input into a list of unique tokens.

    - lowercase
    - split on non-word chars
    - keep tokens with length >= 3 (configurable)
    - return unique tokens preserving order
    """
    if not text:
        return []
    text = text.lower()
    parts = re.split(r'[^a-z0-9]+', text)
    seen = set()
    out = []
    for p in parts:
        p = p.strip()
        if len(p) < 3:
            continue
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def best_match_ratio(token: Optional[str], token_list: List[str]) -> float:
    """Return the highest difflib ratio between token and any token in token_list.
    If token is empty or token_list empty, returns 0.0.
    Ratio is in range [0.0, 1.0].
    """
    if not token or not token_list:
        return 0.0
    best = 0.0
    for t in token_list:
        try:
            r = difflib.SequenceMatcher(None, token, t).ratio()
        except Exception:
            r = 0.0
        if r > best:
            best = r
    return best
