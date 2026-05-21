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
from typing import Any, Callable
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
    unexpected_fields: tuple[str, ...] = ()
    validator: Callable[[dict[str, Any]], None] | None = None


def require_value(payload: dict[str, Any], field: str, expected: Any, case_name: str) -> None:
    actual = payload.get(field)
    if actual != expected:
        raise AssertionError(f"{case_name}: expected {field}={expected!r}, got {actual!r}")


def require_risky_analysis(payload: dict[str, Any], case_name: str) -> None:
    require_value(payload, "verdict", "suspicious", case_name)
    if payload.get("risk_level") not in {"medium", "high"}:
        raise AssertionError(
            f"{case_name}: expected medium/high risk_level, got {payload.get('risk_level')!r}"
        )
    if not isinstance(payload.get("risk_score"), int) or payload["risk_score"] < 50:
        raise AssertionError(
            f"{case_name}: expected risk_score >= 50, got {payload.get('risk_score')!r}"
        )
    if payload.get("experimental_model") is None:
        raise AssertionError(f"{case_name}: expected experimental_model comparison context.")


def validate_root(payload: dict[str, Any]) -> None:
    if payload.get("status") not in {"ok", "running"}:
        raise AssertionError(f"root: expected status ok/running, got {payload.get('status')!r}")
    endpoints = payload.get("available_endpoints")
    expected = {"/health", "/analyze/url", "/analyze/message", "/analyze/malware"}
    if not isinstance(endpoints, list) or not expected.issubset(set(endpoints)):
        raise AssertionError("root: available_endpoints does not include the demo API contract.")


def validate_health(payload: dict[str, Any]) -> None:
    require_value(payload, "status", "ok", "health")


def validate_url_analysis(payload: dict[str, Any]) -> None:
    require_risky_analysis(payload, "url analysis")


def validate_message_analysis(payload: dict[str, Any]) -> None:
    require_risky_analysis(payload, "message analysis")


def validate_malware_analysis(payload: dict[str, Any]) -> None:
    if payload.get("experimental_model") is not None:
        raise AssertionError("malware analysis: experimental_model must stay null.")
    if payload.get("label") not in {"benign", "malware"}:
        raise AssertionError(
            f"malware analysis: expected label benign/malware, got {payload.get('label')!r}"
        )
    if not isinstance(payload.get("is_malware"), bool):
        raise AssertionError("malware analysis: is_malware must be a boolean.")
    if not isinstance(payload.get("confidence"), (int, float)):
        raise AssertionError("malware analysis: confidence must be numeric.")
    probabilities = payload.get("probabilities")
    if not isinstance(probabilities, dict) or {"benign", "malware"} - set(probabilities):
        raise AssertionError("malware analysis: probabilities must include benign and malware.")
    if payload.get("risk_level") not in {"low", "medium", "high"}:
        raise AssertionError(
            "malware analysis: expected low/medium/high risk_level, "
            f"got {payload.get('risk_level')!r}"
        )


CASES = (
    SmokeCase(
        name="root",
        method="GET",
        path="/",
        payload=None,
        expected_status=200,
        expected_fields=("name", "version", "status", "available_endpoints"),
        validator=validate_root,
    ),
    SmokeCase(
        name="health",
        method="GET",
        path="/health",
        payload=None,
        expected_status=200,
        expected_fields=("status", "service"),
        validator=validate_health,
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
        validator=validate_url_analysis,
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
        validator=validate_message_analysis,
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
        validator=validate_malware_analysis,
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

    unexpected = [field for field in case.unexpected_fields if field in payload]
    if unexpected:
        raise AssertionError(f"{case.name}: unexpected fields: {', '.join(unexpected)}")

    if case.validator is not None:
        case.validator(payload)

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
