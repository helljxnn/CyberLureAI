from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from backend.app.schemas.analysis_signal import AnalysisSignal
from backend.app.schemas.message_analysis import MessageAnalysisResponse
from backend.app.schemas.url_analysis import URLAnalysisResponse
from backend.app.services.message_analyzer import analyze_message
from backend.app.services.url_analyzer import analyze_url


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SAMPLE_FILES = {
    "url": PROJECT_ROOT / "data" / "examples" / "url_samples.csv",
    "message": PROJECT_ROOT / "data" / "examples" / "message_samples.csv",
}
REQUIRED_SAMPLE_COLUMNS = {"sample_id", "input", "expected_verdict", "expected_signal"}
VERDICT_RANKS = {
    "likely_safe": 0,
    "review": 1,
    "suspicious": 2,
}
SEVERITIES = ("info", "low", "medium", "high")

AnalysisResponse = URLAnalysisResponse | MessageAnalysisResponse
Analyzer = Callable[[str], AnalysisResponse]


@dataclass(frozen=True)
class LabeledExample:
    sample_type: str
    sample_id: str
    input_value: str
    expected_verdict: str
    expected_signal: str


@dataclass(frozen=True)
class CalibrationResult:
    sample_type: str
    sample_id: str
    input_value: str
    expected_verdict: str
    actual_verdict: str
    verdict_status: str
    expected_signal: str
    expected_signal_found: bool
    risk_level: str
    risk_score: int
    signals: tuple[AnalysisSignal, ...]

    @property
    def signal_codes(self) -> tuple[str, ...]:
        return tuple(signal.code for signal in self.signals)


def load_labeled_examples(path: Path, sample_type: str) -> list[LabeledExample]:
    with path.open(newline="", encoding="utf-8") as sample_file:
        reader = csv.DictReader(sample_file)
        fieldnames = set(reader.fieldnames or ())
        missing_columns = REQUIRED_SAMPLE_COLUMNS - fieldnames
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{path} is missing required columns: {missing}")

        return [
            LabeledExample(
                sample_type=sample_type,
                sample_id=row["sample_id"],
                input_value=row["input"],
                expected_verdict=row["expected_verdict"],
                expected_signal=row["expected_signal"],
            )
            for row in reader
        ]


def evaluate_default_calibration() -> list[CalibrationResult]:
    results: list[CalibrationResult] = []
    for sample_type, path in DEFAULT_SAMPLE_FILES.items():
        results.extend(evaluate_calibration_file(path, sample_type))
    return results


def evaluate_calibration_file(path: Path, sample_type: str) -> list[CalibrationResult]:
    return evaluate_labeled_examples(load_labeled_examples(path, sample_type))


def evaluate_labeled_examples(
    examples: list[LabeledExample],
) -> list[CalibrationResult]:
    return [_evaluate_labeled_example(example) for example in examples]


def summarize_calibration_results(
    results: list[CalibrationResult],
) -> dict[str, object]:
    status_counts = {"correct": 0, "false_positive": 0, "false_negative": 0}
    type_counts: dict[str, int] = {}
    needs_review: list[dict[str, object]] = []

    for result in results:
        status_counts[result.verdict_status] += 1
        type_counts[result.sample_type] = type_counts.get(result.sample_type, 0) + 1

        if result.verdict_status != "correct" or not result.expected_signal_found:
            needs_review.append(_calibration_result_to_report_row(result))

    total = len(results)
    verdict_matches = status_counts["correct"]
    signal_matches = sum(result.expected_signal_found for result in results)

    return {
        "total": total,
        "by_sample_type": type_counts,
        "verdict_status_counts": status_counts,
        "verdict_matches": verdict_matches,
        "signal_matches": signal_matches,
        "verdict_accuracy": verdict_matches / total if total else 0,
        "signal_match_rate": signal_matches / total if total else 0,
        "needs_review": needs_review,
    }


def build_calibration_report_rows(
    results: list[CalibrationResult],
) -> list[dict[str, object]]:
    return [_calibration_result_to_report_row(result) for result in results]


def build_feature_rows(
    results: list[CalibrationResult],
    signal_codes: tuple[str, ...] | None = None,
) -> list[dict[str, object]]:
    stable_signal_codes = signal_codes or collect_signal_codes(results)
    return [
        _calibration_result_to_feature_row(result, stable_signal_codes)
        for result in results
    ]


def collect_signal_codes(results: list[CalibrationResult]) -> tuple[str, ...]:
    return tuple(
        sorted({signal.code for result in results for signal in result.signals})
    )


def write_rows_csv(rows: list[dict[str, object]], output_path: Path) -> None:
    if not rows:
        raise ValueError("Cannot write an empty CSV.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _evaluate_labeled_example(example: LabeledExample) -> CalibrationResult:
    analyzer = _analyzer_for_sample_type(example.sample_type)
    analysis = analyzer(example.input_value)
    signal_codes = {signal.code for signal in analysis.signals}
    expected_signal_found = example.expected_signal in signal_codes

    return CalibrationResult(
        sample_type=example.sample_type,
        sample_id=example.sample_id,
        input_value=example.input_value,
        expected_verdict=example.expected_verdict,
        actual_verdict=analysis.verdict,
        verdict_status=_classify_verdict_result(
            example.expected_verdict,
            analysis.verdict,
        ),
        expected_signal=example.expected_signal,
        expected_signal_found=expected_signal_found,
        risk_level=analysis.risk_level,
        risk_score=analysis.risk_score,
        signals=tuple(analysis.signals),
    )


def _classify_verdict_result(expected_verdict: str, actual_verdict: str) -> str:
    expected_rank = _verdict_rank(expected_verdict)
    actual_rank = _verdict_rank(actual_verdict)

    if actual_rank == expected_rank:
        return "correct"
    if actual_rank > expected_rank:
        return "false_positive"
    return "false_negative"


def _verdict_rank(verdict: str) -> int:
    try:
        return VERDICT_RANKS[verdict]
    except KeyError as exc:
        raise ValueError(f"Unknown verdict: {verdict}") from exc


def _analyzer_for_sample_type(sample_type: str) -> Analyzer:
    if sample_type == "url":
        return analyze_url
    if sample_type == "message":
        return analyze_message
    raise ValueError(f"Unknown sample type: {sample_type}")


def _calibration_result_to_report_row(
    result: CalibrationResult,
) -> dict[str, object]:
    return {
        "sample_type": result.sample_type,
        "sample_id": result.sample_id,
        "input": result.input_value,
        "expected_verdict": result.expected_verdict,
        "actual_verdict": result.actual_verdict,
        "verdict_status": result.verdict_status,
        "expected_signal": result.expected_signal,
        "expected_signal_found": result.expected_signal_found,
        "actual_signal_codes": "|".join(result.signal_codes),
        "risk_level": result.risk_level,
        "risk_score": result.risk_score,
    }


def _calibration_result_to_feature_row(
    result: CalibrationResult,
    signal_codes: tuple[str, ...],
) -> dict[str, object]:
    present_codes = set(result.signal_codes)
    severity_counts = {
        severity: sum(signal.severity == severity for signal in result.signals)
        for severity in SEVERITIES
    }

    row: dict[str, object] = {
        "sample_type": result.sample_type,
        "sample_id": result.sample_id,
        "input": result.input_value,
        "expected_verdict": result.expected_verdict,
        "actual_verdict": result.actual_verdict,
        "risk_level": result.risk_level,
        "risk_score": result.risk_score,
        "signal_count": len(result.signals),
        "signal_score_total": sum(signal.score for signal in result.signals),
    }

    for severity in SEVERITIES:
        row[f"{severity}_signal_count"] = severity_counts[severity]

    for signal_code in signal_codes:
        row[f"signal_{signal_code}"] = int(signal_code in present_codes)

    return row


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate labeled calibration examples and export feature rows.",
    )
    parser.add_argument(
        "--report-csv",
        type=Path,
        help="Optional path for a CSV with per-example calibration results.",
    )
    parser.add_argument(
        "--features-csv",
        type=Path,
        help="Optional path for a CSV with tabular signal features.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    results = evaluate_default_calibration()
    summary = summarize_calibration_results(results)

    print(f"Calibration examples: {summary['total']}")
    print(f"Verdict matches: {summary['verdict_matches']}")
    print(f"Expected signal matches: {summary['signal_matches']}")
    print(f"False positives: {summary['verdict_status_counts']['false_positive']}")
    print(f"False negatives: {summary['verdict_status_counts']['false_negative']}")

    if args.report_csv:
        write_rows_csv(build_calibration_report_rows(results), args.report_csv)
        print(f"Wrote calibration report: {args.report_csv}")

    if args.features_csv:
        write_rows_csv(build_feature_rows(results), args.features_csv)
        print(f"Wrote feature rows: {args.features_csv}")


if __name__ == "__main__":
    main()
