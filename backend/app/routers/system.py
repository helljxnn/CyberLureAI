import csv
from pathlib import Path

from fastapi import APIRouter

from backend.app.core.settings import get_settings


router = APIRouter(tags=["system"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = PROJECT_ROOT / "reports"


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


def _read_csv_rows(file: Path) -> list[dict[str, str]]:
    if not file.exists():
        return []
    with open(file, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@router.get("/system/metrics")
def get_system_metrics() -> dict[str, object]:
    sample_metrics_file = REPORTS_DIR / "baseline_sample_type_metrics_external.csv"
    if not sample_metrics_file.exists():
        sample_metrics_file = REPORTS_DIR / "baseline_sample_type_metrics.csv"

    class_metrics_file = REPORTS_DIR / "baseline_class_metrics_external.csv"
    if not class_metrics_file.exists():
        class_metrics_file = REPORTS_DIR / "baseline_class_metrics.csv"

    return {
        "sample_type": _read_csv_rows(sample_metrics_file),
        "class_metrics": _read_csv_rows(class_metrics_file),
    }
