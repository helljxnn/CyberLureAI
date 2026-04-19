from fastapi import FastAPI

from backend.app.core.settings import get_settings
from backend.app.routers.analysis import router as analysis_router
from backend.app.routers.system import router as system_router

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.app_version,
    description="Initial backend API for CyberLureAI.",
    debug=settings.debug,
)

app.include_router(system_router)
app.include_router(analysis_router)
