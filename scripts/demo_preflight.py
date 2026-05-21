from __future__ import annotations

"""Run the repeatable local demo preflight checks.

Default checks:

    .venv\\Scripts\\python.exe scripts\\demo_preflight.py

Optional endpoint smoke check, with the backend already running:

    .venv\\Scripts\\python.exe scripts\\demo_preflight.py --with-smoke
"""

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"


@dataclass(frozen=True)
class PreflightStep:
    name: str
    command: list[str]
    cwd: Path


def run_step(step: PreflightStep) -> None:
    print(f"\n== {step.name} ==", flush=True)
    print(f"$ {' '.join(step.command)}", flush=True)
    completed = subprocess.run(step.command, cwd=step.cwd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"{step.name} failed with exit code {completed.returncode}.")


def get_npm_command() -> str:
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if npm is None:
        raise RuntimeError("Could not find npm in PATH.")
    return npm


def build_steps(with_smoke: bool, base_url: str) -> list[PreflightStep]:
    steps = [
        PreflightStep(
            name="Backend tests",
            command=[sys.executable, "-m", "pytest"],
            cwd=PROJECT_ROOT,
        ),
        PreflightStep(
            name="Frontend production build",
            command=[get_npm_command(), "run", "-s", "build"],
            cwd=FRONTEND_DIR,
        ),
    ]

    if with_smoke:
        steps.append(
            PreflightStep(
                name="Backend endpoint smoke check",
                command=[
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "demo_smoke_check.py"),
                    "--base-url",
                    base_url,
                ],
                cwd=PROJECT_ROOT,
            )
        )

    return steps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CyberLureAI local demo preflight checks.")
    parser.add_argument(
        "--with-smoke",
        action="store_true",
        help="Also run the API smoke check. Requires the backend to be running.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Backend base URL for --with-smoke. Default: {DEFAULT_BASE_URL}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for step in build_steps(args.with_smoke, args.base_url):
        run_step(step)

    print("\nPreflight passed.")
    if not args.with_smoke:
        print("Start the backend and rerun with --with-smoke to verify live endpoints.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"\n[fail] {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
