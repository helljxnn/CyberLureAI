from pydantic import BaseModel, Field, HttpUrl

from backend.app.schemas.analysis_signal import AnalysisSignal


class URLAnalysisRequest(BaseModel):
    url: HttpUrl = Field(
        ...,
        examples=["http://secure-login-example.com/verify"],
        description="URL to analyze for phishing indicators.",
    )


class URLAnalysisResponse(BaseModel):
    url: HttpUrl
    risk_level: str
    risk_score: int
    verdict: str
    explanation: str
    recommended_action: str
    reasons: list[str]
    signals: list[AnalysisSignal] = Field(default_factory=list)
