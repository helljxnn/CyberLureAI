from fastapi import FastAPI

from backend.app.schemas.message_analysis import (
    MessageAnalysisRequest,
    MessageAnalysisResponse,
)
from backend.app.schemas.url_analysis import URLAnalysisRequest, URLAnalysisResponse
from backend.app.services.message_analyzer import analyze_message
from backend.app.services.url_analyzer import analyze_url


app = FastAPI(
    title="CyberLureAI API",
    version="0.1.0",
    description="Initial backend API for CyberLureAI.",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "CyberLureAI API",
    }


@app.post("/analyze/url", response_model=URLAnalysisResponse, tags=["analysis"])
def analyze_suspicious_url(payload: URLAnalysisRequest) -> URLAnalysisResponse:
    return analyze_url(payload.url)


@app.post("/analyze/message", response_model=MessageAnalysisResponse, tags=["analysis"])
def analyze_suspicious_message(payload: MessageAnalysisRequest) -> MessageAnalysisResponse:
    return analyze_message(payload.message)
