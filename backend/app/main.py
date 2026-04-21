from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.error_handlers import register_error_handlers
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [settings.frontend_url],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(system_router)
app.include_router(analysis_router)
