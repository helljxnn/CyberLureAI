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


@router.get("/system/metrics")
def get_system_metrics() -> dict[str, object]:
    import csv
    from pathlib import Path
    
    project_root = Path(__file__).resolve().parents[3]
    reports_dir = project_root / "reports"
    
    sample_metrics_file = reports_dir / "baseline_sample_type_metrics_external.csv"
    if not sample_metrics_file.exists():
        sample_metrics_file = reports_dir / "baseline_sample_type_metrics.csv"
        
    class_metrics_file = reports_dir / "baseline_class_metrics_external.csv"
    if not class_metrics_file.exists():
        class_metrics_file = reports_dir / "baseline_class_metrics.csv"
        
    metrics = {
        "sample_type": [],
        "class_metrics": []
    }
    
    if sample_metrics_file.exists():
        with open(sample_metrics_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            metrics["sample_type"] = [row for row in reader]
            
    if class_metrics_file.exists():
        with open(class_metrics_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            metrics["class_metrics"] = [row for row in reader]
            
    return metrics
