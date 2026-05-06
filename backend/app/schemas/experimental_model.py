from pydantic import BaseModel, Field


class ExperimentalModelAnalysis(BaseModel):
    status: str = Field(
        ...,
        description="Experimental model status: available or unavailable.",
    )
    strategy: str
    sample_type: str
    verdict: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    agrees_with_heuristic: bool | None = None
    note: str
