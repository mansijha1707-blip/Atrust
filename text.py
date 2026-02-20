import re

SCAM_RULES = [
    (r"\burgent\b", "text:urgent_language", 3),
    (r"don[’']?t tell", "text:secrecy_request", 4),
    (r"\botp\b", "text:otp_mentioned", 5),
    (r"\bupi\b", "text:upi_mentioned", 5),
    (r"transfer now|send now|pay now", "text:immediate_transfer", 4),
    (r"police case|fir|legal notice|warrant", "text:legal_threat", 4),
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
            matches.append({"pattern": pattern, "flag": flag, "severity": sev})

    if matches:
        evidence.append({
            "pipeline": "text",
            "type": "scam_intent_rules",
            "severity": 4 if any(m["severity"] >= 5 for m in matches) else 3,
            "details": {"matches": matches},
            "timestamps": []
        })

    return {"penalty": min(penalty, 60), "flags": flags, "evidence": evidence, "summary": {"match_count": len(matches)}}
