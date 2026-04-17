from fastapi import FastAPI

from backend.app.routers.analysis import router as analysis_router
from backend.app.routers.system import router as system_router


app = FastAPI(
    title="CyberLureAI API",
    version="0.1.0",
    description="Initial backend API for CyberLureAI.",
)

app.include_router(system_router)
app.include_router(analysis_router)
