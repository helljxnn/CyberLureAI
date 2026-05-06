from __future__ import annotations

from functools import lru_cache

from backend.app.schemas.analysis_signal import AnalysisSignal
from backend.app.schemas.experimental_model import ExperimentalModelAnalysis
from backend.app.services.baseline_classifier import (
    SEPARATE_STRATEGY,
    build_feature_matrix,
    fit_separate_baseline_classifiers,
)
from backend.app.services.calibration import SEVERITIES


EXPERIMENTAL_MODEL_NOTE = (
    "Experimental calibration model for comparison only; the explainable "
    "heuristic verdict remains the primary API behavior."
)


def compare_with_experimental_baseline(
    *,
    sample_type: str,
    heuristic_verdict: str,
    risk_level: str,
    risk_score: int,
    signals: list[AnalysisSignal],
) -> ExperimentalModelAnalysis:
    try:
        bundle = _load_separate_baseline_bundle()
        model = bundle["models"].get(sample_type)
        if model is None:
            return _unavailable(sample_type, f"No {sample_type} baseline is available.")

        feature_names = bundle["feature_names"]
        feature_row = _build_analysis_feature_row(
            sample_type=sample_type,
            risk_level=risk_level,
            risk_score=risk_score,
            signals=signals,
        )
        feature_matrix = build_feature_matrix([feature_row], feature_names)
        verdict = str(model.predict(feature_matrix)[0])
        confidence = _prediction_confidence(model, feature_matrix)

        return ExperimentalModelAnalysis(
            status="available",
            strategy=SEPARATE_STRATEGY,
            sample_type=sample_type,
            verdict=verdict,
            confidence=confidence,
            agrees_with_heuristic=verdict == heuristic_verdict,
            note=EXPERIMENTAL_MODEL_NOTE,
        )
    except Exception as exc:
        return _unavailable(sample_type, f"Experimental baseline unavailable: {exc}")


@lru_cache(maxsize=1)
def _load_separate_baseline_bundle() -> dict[str, object]:
    return fit_separate_baseline_classifiers()


def _build_analysis_feature_row(
    *,
    sample_type: str,
    risk_level: str,
    risk_score: int,
    signals: list[AnalysisSignal],
) -> dict[str, object]:
    present_codes = {signal.code for signal in signals}
    severity_counts = {
        severity: sum(signal.severity == severity for signal in signals)
        for severity in SEVERITIES
    }

    row: dict[str, object] = {
        "sample_type": sample_type,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "signal_count": len(signals),
        "signal_score_total": sum(signal.score for signal in signals),
    }

    for severity in SEVERITIES:
        row[f"{severity}_signal_count"] = severity_counts[severity]

    for signal_code in _model_signal_codes():
        row[f"signal_{signal_code}"] = int(signal_code in present_codes)

    return row


def _model_signal_codes() -> tuple[str, ...]:
    feature_names = _load_separate_baseline_bundle()["feature_names"]
    return tuple(
        feature_name.removeprefix("signal_")
        for feature_name in feature_names
        if feature_name.startswith("signal_")
    )


def _prediction_confidence(model: object, feature_matrix: list[list[float]]) -> float | None:
    if not hasattr(model, "predict_proba"):
        return None

    probabilities = model.predict_proba(feature_matrix)[0]
    return round(float(max(probabilities)), 3)


def _unavailable(sample_type: str, reason: str) -> ExperimentalModelAnalysis:
    return ExperimentalModelAnalysis(
        status="unavailable",
        strategy=SEPARATE_STRATEGY,
        sample_type=sample_type,
        note=reason,
    )
