from fastapi import APIRouter

from backend.app.schemas.message_analysis import (
    MessageAnalysisRequest,
    MessageAnalysisResponse,
)
from backend.app.schemas.url_analysis import URLAnalysisRequest, URLAnalysisResponse
from backend.app.services.message_analyzer import analyze_message
from backend.app.services.url_analyzer import analyze_url


router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/url", response_model=URLAnalysisResponse)
def analyze_suspicious_url(payload: URLAnalysisRequest) -> URLAnalysisResponse:
    return analyze_url(str(payload.url))


@router.post("/message", response_model=MessageAnalysisResponse)
def analyze_suspicious_message(payload: MessageAnalysisRequest) -> MessageAnalysisResponse:
    return analyze_message(payload.message)
