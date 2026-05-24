from pydantic import BaseModel
from typing import Optional, Literal

class FeedbackRequest(BaseModel):
    sample_type: Literal["url", "message", "malware"]
    input_data: str
    verdict_given: str
    user_feedback: Literal["correct", "incorrect"]
    comments: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    message: str
