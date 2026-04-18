from fastapi import APIRouter


router = APIRouter(tags=["system"])


@router.get("/")
def root() -> dict[str, object]:
    return {
        "name": "CyberLureAI API",
        "version": "0.1.0",
        "status": "running",
        "docs_url": "/docs",
        "available_endpoints": [
            "/health",
            "/analyze/url",
            "/analyze/message",
        ],
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "CyberLureAI API",
    }
