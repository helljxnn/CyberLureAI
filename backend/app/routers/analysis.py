from fastapi import APIRouter

from backend.app.schemas.message_analysis import (
    MessageAnalysisRequest,
    MessageAnalysisResponse,
)
from backend.app.schemas.url_analysis import URLAnalysisRequest, URLAnalysisResponse
from backend.app.services.experimental_baseline import (
    compare_with_experimental_baseline,
)
from backend.app.services.message_analyzer import analyze_message
from backend.app.services.url_analyzer import analyze_url


router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/url", response_model=URLAnalysisResponse)
def analyze_suspicious_url(payload: URLAnalysisRequest) -> URLAnalysisResponse:
    analysis = analyze_url(str(payload.url))
    analysis.experimental_model = compare_with_experimental_baseline(
        sample_type="url",
        heuristic_verdict=analysis.verdict,
        risk_level=analysis.risk_level,
        risk_score=analysis.risk_score,
        signals=analysis.signals,
    )
    return analysis


@router.post("/message", response_model=MessageAnalysisResponse)
def analyze_suspicious_message(payload: MessageAnalysisRequest) -> MessageAnalysisResponse:
    analysis = analyze_message(payload.message)
    analysis.experimental_model = compare_with_experimental_baseline(
        sample_type="message",
        heuristic_verdict=analysis.verdict,
        risk_level=analysis.risk_level,
        risk_score=analysis.risk_score,
        signals=analysis.signals,
    )
    return analysis
