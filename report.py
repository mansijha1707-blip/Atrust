from typing import Dict, Any, List
from .schemas import TrustReport, EvidenceItem

def _risk_bucket(score: int) -> str:
    if score >= 85: return "low"
    if score >= 65: return "medium"
    if score >= 40: return "high"
    return "critical"

def _action(risk_type: str) -> str:
    return {
        "low": "Proceed normally. Keep original sources and context.",
        "medium": "Proceed with caution. Verify via an independent channel.",
        "high": "Do not act immediately. Seek verification and avoid sharing.",
        "critical": "Treat as malicious. Do not send money/OTP/UPI or sensitive info."
    }[risk_type]

def build_trust_report(results: Dict[str, Any]) -> TrustReport:
    evidence: List[EvidenceItem] = []
    flags: List[str] = []
    penalty = 0

    # Each pipeline can contribute evidence + penalty
    for key in ("video", "image", "audio", "text"):
        r = results.get(key) or {}
        for ev in r.get("evidence", []):
            evidence.append(EvidenceItem(**ev))
        flags.extend(r.get("flags", []))
        penalty += int(r.get("penalty", 0))

    # clamp + compute
    trust_score = max(0, min(100, 100 - penalty))
    risk_type = _risk_bucket(trust_score)
    recommended_action = _action(risk_type)

    # de-dupe flags
    flags = sorted(set(flags))

    return TrustReport(
        trust_score=trust_score,
        risk_type=risk_type, flags=flags,
        evidence=evidence,
        recommended_action=recommended_action,
        raw=results
    )
