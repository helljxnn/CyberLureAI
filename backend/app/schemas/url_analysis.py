from pydantic import BaseModel, HttpUrl


class URLAnalysisRequest(BaseModel):
    url: HttpUrl


class URLAnalysisResponse(BaseModel):
    url: HttpUrl
    risk_level: str
    risk_score: int
    verdict: str
    explanation: str
    recommended_action: str
    reasons: list[str]
