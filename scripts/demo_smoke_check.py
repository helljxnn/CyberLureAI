from __future__ import annotations

"""Smoke-check the local CyberLureAI demo API.

Run this after starting the backend with:

    uvicorn backend.app.main:app --reload
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.schemas.malware_analysis import MALWARE_FEATURE_EXAMPLE


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class SmokeCase:
    name: str
    method: str
    path: str
    payload: dict[str, Any] | None
    expected_status: int
    expected_fields: tuple[str, ...]


CASES = (
    SmokeCase(
        name="root",
        method="GET",
        path="/",
        payload=None,
        expected_status=200,
        expected_fields=("name", "version", "status", "available_endpoints"),
    ),
    SmokeCase(
        name="health",
        method="GET",
        path="/health",
        payload=None,
        expected_status=200,
        expected_fields=("status", "service"),
    ),
    SmokeCase(
        name="url analysis",
        method="POST",
        path="/analyze/url",
        payload={"url": "http://secure-login-bank-verify.example.com"},
        expected_status=200,
        expected_fields=(
            "url",
            "risk_level",
            "risk_score",
            "verdict",
            "reasons",
            "signals",
            "experimental_model",
        ),
    ),
    SmokeCase(
        name="message analysis",
        method="POST",
        path="/analyze/message",
        payload={
            "message": (
                "Urgent: verify your bank account now by clicking "
                "https://fake-bank-alert.example"
            )
        },
        expected_status=200,
        expected_fields=(
            "message",
            "risk_level",
            "risk_score",
            "verdict",
            "reasons",
            "signals",
            "experimental_model",
        ),
    ),
    SmokeCase(
        name="malware analysis",
        method="POST",
        path="/analyze/malware",
        payload={"features": MALWARE_FEATURE_EXAMPLE},
        expected_status=200,
        expected_fields=(
            "is_malware",
            "label",
            "confidence",
            "probabilities",
            "risk_level",
            "risk_score",
            "verdict",
            "reasons",
            "signals",
        ),
    ),
)


def request_json(base_url: str, case: SmokeCase) -> tuple[int, dict[str, Any]]:
    body = None
    headers = {"Accept": "application/json"}
    if case.payload is not None:
        body = json.dumps(case.payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        f"{base_url.rstrip('/')}{case.path}",
        data=body,
        headers=headers,
        method=case.method,
    )

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw)
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        payload = json.loads(raw) if raw else {}
        return exc.code, payload
    except URLError as exc:
        raise RuntimeError(
            f"Could not reach {base_url}. Start the backend before running this check."
        ) from exc


def validate_case(base_url: str, case: SmokeCase) -> None:
    status, payload = request_json(base_url, case)
    if status != case.expected_status:
        raise AssertionError(
            f"{case.name}: expected HTTP {case.expected_status}, got {status}. "
            f"Response: {payload}"
        )

    missing = [field for field in case.expected_fields if field not in payload]
    if missing:
        raise AssertionError(f"{case.name}: missing fields: {', '.join(missing)}")

    print(f"[ok] {case.name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-check the local CyberLureAI demo API.")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Backend base URL. Default: {DEFAULT_BASE_URL}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for case in CASES:
        validate_case(args.base_url, case)

    print(f"Smoke check passed for {args.base_url.rstrip('/')}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
