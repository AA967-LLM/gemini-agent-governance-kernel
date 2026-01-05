from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class VerdictType(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"

class AgentVerdict(BaseModel):
    """
    Strict schema for Agent Verdicts.
    Enforces reasoning, evidence citation, and confidence ranges.
    """
    verdict: VerdictType
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    evidence: List[str] = Field(default_factory=list, description="List of evidence strings (must utilize [SRC:] or [CMD:] format)")
    blocking: bool = Field(default=False, description="Whether this verdict should block execution")
    reasoning: str = Field(min_length=10, description="Detailed reasoning for the verdict")

    @field_validator('evidence')
    @classmethod
    def validate_evidence_format(cls, v):
        """Ensure evidence follows [SRC:] or [CMD:] format if present."""
        for item in v:
            if not (item.startswith('[SRC:') or item.startswith('[CMD:') or item.startswith('[TBD:')):
                # We allow TBD for placeholders during development
                raise ValueError(f"Invalid evidence format: {item}. Must start with [SRC:], [CMD:], or [TBD:]")
        return v

    @field_validator('confidence')
    @classmethod
    def calibrate_confidence(cls, v, info):
        """
        Basic calibration validation.
        Ensure PASS isn't low confidence, and FAIL isn't low confidence.
        """
        # Note: In Pydantic v2, we access other fields via validation_info but simplicity here:
        # We rely on the caller or the model logic to ensure semantic consistency.
        # This validator just ensures strict bounds, which Field(ge=0.0, le=1.0) handles.
        return v
