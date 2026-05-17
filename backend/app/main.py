from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from backend.app.core.error_handlers import register_error_handlers
from backend.app.core.settings import get_settings
from backend.app.routers.analysis import router as analysis_router
from backend.app.routers.system import router as system_router
from backend.app.services.experimental_baseline import warm_up_baseline_model

logger = logging.getLogger(__name__)

settings = get_settings()

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Warming up experimental baseline model at startup...")
    warm_up_baseline_model()
    logger.info("Experimental baseline model ready.")
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.app_version,
    description="Initial backend API for CyberLureAI.",
    debug=settings.debug,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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

FRONTEND_DIST = Path(__file__).resolve().parents[3] / "frontend" / "dist"
if settings.serve_frontend and FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
    logger.info(f"Serving frontend from {FRONTEND_DIST}")
