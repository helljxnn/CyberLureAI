from pydantic import BaseModel


class MessageAnalysisRequest(BaseModel):
    message: str


class MessageAnalysisResponse(BaseModel):
    message: str
    risk_level: str
    risk_score: int
    verdict: str
    explanation: str
    recommended_action: str
    reasons: list[str]
