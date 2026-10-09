import re

PATTERNS = {
    "secret": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),             # cloud access-key style
    "pan": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),           # Indian PAN format
    "aadhaar": re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b"),         # Aadhaar-style grouping
    "code": re.compile(r"(com\.acme\.internal|acme_internal)"),  # internal package markers
    "conf": re.compile(r"CONFIDENTIAL\s*-\s*Acme Internal"),   # classification banner
}
CARD_CANDIDATE = re.compile(r"\b\d{16}\b")


def luhn_ok(number: str) -> bool:
    """Validate a digit string with the Luhn algorithm."""
    total = 0
    for i, ch in enumerate(reversed(number)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def dlp_hit(text: str) -> bool:
    """Return True if any DLP rule fires on the prompt text."""
    if any(p.search(text) for p in PATTERNS.values()):
        return True
    return any(luhn_ok(m) for m in CARD_CANDIDATE.findall(text))
