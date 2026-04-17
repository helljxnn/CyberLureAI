from pydantic import BaseModel, Field


class MessageAnalysisRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=5,
        examples=["Urgent: verify your bank account now by clicking https://fake-bank-alert.example"],
        description="Message text to analyze for scam or phishing patterns.",
    )


class MessageAnalysisResponse(BaseModel):
    message: str
    risk_level: str
    risk_score: int
    verdict: str
    explanation: str
    recommended_action: str
    reasons: list[str]
