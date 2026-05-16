from fastapi import APIRouter

from backend.app.core.settings import get_settings


router = APIRouter(tags=["system"])


@router.get("/")
def root() -> dict[str, object]:
    settings = get_settings()
    return {
        "name": settings.api_title,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.app_env,
        "docs_url": "/docs",
        "available_endpoints": [
            "/health",
            "/analyze/url",
            "/analyze/message",
            "/analyze/malware",
        ],
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.api_title,
    }
