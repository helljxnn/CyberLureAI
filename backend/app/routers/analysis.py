from fastapi import APIRouter, HTTPException

from backend.app.schemas.malware_analysis import (
    MalwareAnalysisRequest,
    MalwareAnalysisResponse,
)
from backend.app.schemas.message_analysis import (
    MessageAnalysisRequest,
    MessageAnalysisResponse,
)
from backend.app.schemas.url_analysis import URLAnalysisRequest, URLAnalysisResponse
from backend.app.services.experimental_baseline import (
    compare_with_experimental_baseline,
)
from backend.app.services.malware_analyzer import analyze_malware_features
from backend.app.services.malware_response_builder import build_malware_analysis_response
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


@router.post("/malware", response_model=MalwareAnalysisResponse)
def analyze_suspicious_file(payload: MalwareAnalysisRequest) -> MalwareAnalysisResponse:
    try:
        verdict = analyze_malware_features(payload.features)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    payload_data = build_malware_analysis_response(verdict)
    return MalwareAnalysisResponse(
        is_malware=payload_data.is_malware,
        label=payload_data.label,
        confidence=payload_data.confidence,
        probabilities=payload_data.probabilities,
        risk_level=payload_data.risk_level,
        risk_score=payload_data.risk_score,
        verdict=payload_data.verdict,
        explanation=payload_data.explanation,
        recommended_action=payload_data.recommended_action,
        reasons=payload_data.reasons,
        signals=payload_data.signals,
    )
