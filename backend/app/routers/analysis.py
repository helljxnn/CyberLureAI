from fastapi import APIRouter, HTTPException, UploadFile, File

from backend.app.schemas.feedback import FeedbackRequest, FeedbackResponse
from backend.app.services.feedback_service import save_feedback
from backend.app.services.pe_extractor import extract_pe_features
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


@router.post("/malware/upload", response_model=MalwareAnalysisResponse)
async def analyze_malware_file(file: UploadFile = File(...)) -> MalwareAnalysisResponse:
    try:
        content = await file.read()
        features = extract_pe_features(content)
        verdict = analyze_malware_features(features)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error analizando el archivo") from exc

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


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    try:
        save_feedback(payload)
        return FeedbackResponse(status="success", message="Feedback recibido y guardado con éxito.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error guardando feedback") from exc
