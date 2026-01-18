"""
services/brand_consistency.py

Cross-Modal Brand Identity Consistency Analyzer

Implements a rule-based, explainable analyzer that compares the domain token
with tokens extracted from HTML metadata and OCR text. Produces a
consistency score, risk level, mismatches, evidence and a human-friendly
recommendation. No ML, no external APIs. Uses lightweight fuzzy matching.
"""
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import difflib
import re
from models.brand_consistency.utils import (
    normalize_tokens,
    extract_domain_token,
    best_match_ratio,
)


def analyze_brand_consistency(url: str, html_text: str = "", ocr_text: str = "") -> Dict:
    """Analyze brand consistency across domain, HTML and OCR text.

    Inputs:
      - url: target URL (string)
      - html_text: HTML title/meta or extracted textual metadata
      - ocr_text: OCR-extracted text from screenshot

    Returns JSON-serializable dict with:
      - consistency_score: 0..100 (higher == more consistent / safer)
      - risk_level: LOW / MEDIUM / HIGH
      - mismatches: human-readable list
      - evidence: exact tokens found per source
      - recommendation: short guidance string
    """
    # Heuristic weights (tunable): domain_vs_ocr highest
    weights = {
        "domain_vs_ocr": 0.45,
        "domain_vs_html": 0.3,
        "html_vs_ocr": 0.25,
    }

    # Extract domain token
    domain_token = extract_domain_token(url)

    # Extract normalized tokens from html and ocr
    html_tokens = normalize_tokens(html_text)
    ocr_tokens = normalize_tokens(ocr_text)

    # Evidence object
    evidence = {
        "domain_token": domain_token or "",
        "html_tokens": html_tokens,
        "ocr_tokens": ocr_tokens,
    }

    # Compute best match ratios (0..1)
    dom_vs_ocr_ratio = best_match_ratio(domain_token, ocr_tokens)
    dom_vs_html_ratio = best_match_ratio(domain_token, html_tokens)
    html_vs_ocr_ratio = best_match_ratio_list(html_tokens, ocr_tokens)

    # Convert ratios into mismatch scores (1 - ratio)
    dom_vs_ocr_mismatch = 1.0 - dom_vs_ocr_ratio
    dom_vs_html_mismatch = 1.0 - dom_vs_html_ratio
    html_vs_ocr_mismatch = 1.0 - html_vs_ocr_ratio

    # Weighted mismatch
    weighted_mismatch = (
        weights["domain_vs_ocr"] * dom_vs_ocr_mismatch
        + weights["domain_vs_html"] * dom_vs_html_mismatch
        + weights["html_vs_ocr"] * html_vs_ocr_mismatch
    )

    # Consistency score 0..100 (higher is better)
    consistency_score = max(0, int(round((1.0 - weighted_mismatch) * 100)))

    # Determine risk level
    if consistency_score >= 70:
        risk = "LOW"
    elif consistency_score >= 40:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    # Build human-readable mismatches list
    mismatches: List[str] = []
    if dom_vs_ocr_ratio < 0.6:
        mismatches.append("Domain does not match brand mentioned in OCR text.")
    if dom_vs_html_ratio < 0.6:
        mismatches.append("Domain does not match brand mentioned in HTML metadata/title.")
    if html_vs_ocr_ratio < 0.6:
        mismatches.append("HTML metadata and webpage screenshot text disagree on brand.")

    if not mismatches:
        mismatches = ["No major brand inconsistencies detected."]

    # Recommendation generation
    if risk == "HIGH":
        recommendation = "Do not enter credentials. Verify the official domain via known channels."
    elif risk == "MEDIUM":
        recommendation = "Proceed with caution. Manually verify branding and domain before providing sensitive data."
    else:
        recommendation = "Branding appears consistent; use usual caution."

    return {
        "consistency_score": consistency_score,
        "risk_level": risk,
        "mismatches": mismatches,
        "evidence": evidence,
        "recommendation": recommendation,
        "details": {
            "domain_vs_ocr_ratio": round(dom_vs_ocr_ratio, 3),
            "domain_vs_html_ratio": round(dom_vs_html_ratio, 3),
            "html_vs_ocr_ratio": round(html_vs_ocr_ratio, 3),
        },
    }


def best_match_ratio_list(list_a: List[str], list_b: List[str]) -> float:
    """Compute the best pairwise match ratio between tokens in two lists.
    Returns max ratio if any tokens exist, otherwise 0.0.
    """
    best = 0.0
    for a in list_a:
        r = best_match_ratio(a, list_b)
        if r > best:
            best = r
    return best
