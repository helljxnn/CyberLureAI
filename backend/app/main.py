from fastapi import FastAPI


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
