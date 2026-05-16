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

    risk_score = int(verdict.confidence * 100) if verdict.is_malware else int(verdict.probabilities.get("benign", 0.95) * 100)

    if verdict.is_malware:
        risk_level = "high"
        verdict_label = "suspicious"
        recommended = "Do not execute this file. Isolate it for further analysis by a security professional."
        explanation = (
            f"The ML classifier identified this file as {verdict.label} "
            f"with {verdict.confidence:.1%} confidence based on 69 PE header features."
        )
    else:
        confidence = verdict.probabilities.get("benign", 0.95)
        if confidence >= 0.85:
            risk_level = "low"
            verdict_label = "likely_safe"
        elif confidence >= 0.65:
            risk_level = "medium"
            verdict_label = "review"
        else:
            risk_level = "medium"
            verdict_label = "review"
        recommended = "The file appears benign, but keep normal caution. Verify the source before execution."
        explanation = (
            f"The ML classifier identified this file as {verdict.label} "
            f"with {confidence:.1%} confidence based on 69 PE header features."
        )

    signals = [
        {
            "code": "ml_classification",
            "severity": risk_level,
            "score": risk_score,
            "description": f"RandomForest classifier prediction: {verdict.label} ({verdict.confidence:.1%} confidence)",
        },
        {
            "code": "probability_benign",
            "severity": "info",
            "score": int(verdict.probabilities["benign"] * 100),
            "description": f"Probability benign: {verdict.probabilities['benign']:.2%}",
        },
        {
            "code": "probability_malware",
            "severity": risk_level,
            "score": int(verdict.probabilities["malware"] * 100),
            "description": f"Probability malware: {verdict.probabilities['malware']:.2%}",
        },
    ]

    return MalwareAnalysisResponse(
        is_malware=verdict.is_malware,
        label=verdict.label,
        confidence=verdict.confidence,
        probabilities=verdict.probabilities,
        risk_level=risk_level,
        risk_score=risk_score,
        verdict=verdict_label,
        explanation=explanation,
        recommended_action=recommended,
        reasons=[
            f"ML classifier assigned {verdict.confidence:.1%} confidence to the {verdict.label} class.",
            f"Probability distribution: benign={verdict.probabilities['benign']:.2%}, malware={verdict.probabilities['malware']:.2%}.",
        ],
        signals=signals,
    )
