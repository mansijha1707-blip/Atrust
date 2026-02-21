import re

# ── Keyword rules (Indian scam patterns) ─────────────────────────────────────
SCAM_RULES = [
    (r"\burgent\b",                          "text:urgent_language",    3),
    (r"don['']?t tell",                      "text:secrecy_request",    4),
    (r"\botp\b",                             "text:otp_mentioned",      5),
    (r"\bupi\b",                             "text:upi_mentioned",      5),
    (r"transfer now|send now|pay now",       "text:immediate_transfer", 4),
    (r"police case|fir|legal notice|warrant","text:legal_threat",       4),
    (r"\bkyc\b",                             "text:kyc_mentioned",      4),
    (r"account blocked|account suspended",   "text:account_threat",     4),
    (r"click here|click the link",           "text:phishing_link",      3),
    (r"you have won|lottery|prize money",    "text:lottery_scam",       5),
    (r"\bcvv\b|\bpin\b",                     "text:card_details",       5),
    (r"\bneft\b|\bimps\b|\bifsc\b",          "text:bank_details",       4),
    (r"verify your account|reactivate",      "text:account_verify",     3),
    (r"rbi|income tax|irdai|trai|narcotics", "text:impersonation",      5),
    (r"limited time|expires today|act now",  "text:urgency_pressure",   3),
]

def scan_text(text: str):
    t = text.lower()
    penalty = 0
    flags = []
    evidence = []
    matches = []

    for pattern, flag, sev in SCAM_RULES:
        if re.search(pattern, t):
            flags.append(flag)
            penalty += sev * 4
            matches.append({"flag": flag, "severity": sev})

    if matches:
        evidence.append({
            "pipeline": "text",
            "type": "scam_intent_rules",
            "severity": 4 if any(m["severity"] >= 5 for m in matches) else 3,
            "details": {"matches": matches},
            "timestamps": []
        })

    scam_score = min(penalty, 60) / 60.0

    return {
        "penalty": min(penalty, 60),
        "flags": flags,
        "evidence": evidence,
        "summary": {"score": scam_score}
    }
