from dataclasses import dataclass
from functools import lru_cache
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def _get_bool_env(name: str, default: bool) -> bool:
    value = getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int_env(name: str, default: int) -> int:
    value = getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    app_env: str
    debug: bool
    api_host: str
    api_port: int
    frontend_url: str
    data_dir: str
    openai_api_key: str

    @property
    def api_title(self) -> str:
        return f"{self.app_name} API"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=getenv("APP_NAME", "CyberLureAI"),
        app_version=getenv("APP_VERSION", "0.1.0"),
        app_env=getenv("APP_ENV", "development"),
        debug=_get_bool_env("DEBUG", True),
        api_host=getenv("API_HOST", "127.0.0.1"),
        api_port=_get_int_env("API_PORT", 8000),
        frontend_url=getenv("FRONTEND_URL", "http://localhost:3000"),
        data_dir=getenv("DATA_DIR", "./data"),
        openai_api_key=getenv("OPENAI_API_KEY", ""),
    )
