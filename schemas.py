from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

RiskType = Literal["low", "medium", "high", "critical"]
PipelineType = Literal["video", "image", "audio", "text"]

class TimestampWindow(BaseModel):
    start: float
    end: float

class EvidenceItem(BaseModel):
    pipeline: PipelineType
    type: str
    severity: int = Field(ge=1, le=5)
    details: Dict[str, Any] = {}
    timestamps: List[TimestampWindow] = []

class TrustReport(BaseModel):
    trust_score: int = Field(ge=0, le=100)
    risk_type: RiskType
    flags: List[str]
    evidence: List[EvidenceItem]
    recommended_action: str
    raw: Dict[str, Any] = {}
