PHISHING_KEYWORDS = [
    "verify your account",
    "login immediately",
    "urgent action",
    "confirm password",
    "security alert",
    "account suspended",
    "bank verification",
    "click here",
    "update account",
    "provide your",
    "enter your",
]


def is_phishing(text: str, threshold: int = 3):
    """Return (bool, score, matches) indicating whether text looks phishing-like.

    Parameters:
    - text: OCR-extracted text
    - threshold: number of keyword matches required to flag phishing

    Returns:
    - (bool:phishing, int:score, list:matches)
    """
    if not text:
        return False, 0, []
    score = 0
    matches = []
    s = text.lower()
    for kw in PHISHING_KEYWORDS:
        if kw in s:
            score += 1
            matches.append(kw)

    return (score >= int(threshold)), score, matches
