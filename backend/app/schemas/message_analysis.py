from pydantic import BaseModel, Field, field_validator


class MessageAnalysisRequest(BaseModel):
    message: str = Field(
        ...,
        max_length=5000,
        examples=["Urgent: verify your bank account now by clicking https://fake-bank-alert.example"],
        description="Message text to analyze for scam or phishing patterns.",
    )

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 5:
            raise ValueError("Message must contain at least 5 non-space characters.")
        return normalized


class MessageAnalysisResponse(BaseModel):
    message: str
    risk_level: str
    risk_score: int
    verdict: str
    explanation: str
    recommended_action: str
    reasons: list[str]
