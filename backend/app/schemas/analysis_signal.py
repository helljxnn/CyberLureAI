from pydantic import BaseModel, Field


class AnalysisSignal(BaseModel):
    code: str = Field(..., description="Stable identifier for the detected signal.")
    severity: str = Field(..., description="Signal severity: info, low, medium, or high.")
    score: int = Field(..., ge=0, le=100, description="Score contribution from this signal.")
    description: str = Field(..., description="Human-readable explanation for the signal.")
