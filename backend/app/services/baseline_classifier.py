from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from backend.app.services.calibration import (
    CalibrationResult,
    build_feature_rows,
    evaluate_default_calibration,
    write_rows_csv,
)


LABELS = ("likely_safe", "review", "suspicious")
SAMPLE_TYPES = ("message", "url")
DEFAULT_FOLDS = 5


@dataclass(frozen=True)
class BaselinePrediction:
    sample_type: str
    sample_id: str
    expected_verdict: str
    heuristic_verdict: str
    baseline_verdict: str
    heuristic_correct: bool
    baseline_correct: bool


@dataclass(frozen=True)
class BaselineEvaluation:
    total: int
    feature_names: tuple[str, ...]
    heuristic_accuracy: float
    baseline_accuracy: float
    predictions: tuple[BaselinePrediction, ...]

    @property
    def baseline_misses(self) -> tuple[BaselinePrediction, ...]:
        return tuple(
            prediction
            for prediction in self.predictions
            if not prediction.baseline_correct
        )

    @property
    def heuristic_misses(self) -> tuple[BaselinePrediction, ...]:
        return tuple(
            prediction
            for prediction in self.predictions
            if not prediction.heuristic_correct
        )


def evaluate_baseline_classifier(
    results: list[CalibrationResult] | None = None,
    folds: int = DEFAULT_FOLDS,
) -> BaselineEvaluation:
    calibration_results = results or evaluate_default_calibration()
    feature_rows = build_feature_rows(calibration_results)
    feature_names = collect_model_feature_names(feature_rows)
    x_values = build_feature_matrix(feature_rows, feature_names)
    expected_labels = [row["expected_verdict"] for row in feature_rows]
    heuristic_labels = [row["actual_verdict"] for row in feature_rows]
    baseline_labels = _cross_validated_predictions(x_values, expected_labels, folds)

    predictions = tuple(
        BaselinePrediction(
            sample_type=str(row["sample_type"]),
            sample_id=str(row["sample_id"]),
            expected_verdict=str(expected),
            heuristic_verdict=str(heuristic),
            baseline_verdict=str(baseline),
            heuristic_correct=heuristic == expected,
            baseline_correct=baseline == expected,
        )
        for row, expected, heuristic, baseline in zip(
            feature_rows,
            expected_labels,
            heuristic_labels,
            baseline_labels,
            strict=True,
        )
    )

    return BaselineEvaluation(
        total=len(feature_rows),
        feature_names=feature_names,
        heuristic_accuracy=accuracy_score(expected_labels, heuristic_labels),
        baseline_accuracy=accuracy_score(expected_labels, baseline_labels),
        predictions=predictions,
    )


def fit_baseline_classifier(
    results: list[CalibrationResult] | None = None,
) -> dict[str, object]:
    calibration_results = results or evaluate_default_calibration()
    feature_rows = build_feature_rows(calibration_results)
    feature_names = collect_model_feature_names(feature_rows)
    x_values = build_feature_matrix(feature_rows, feature_names)
    y_values = [row["expected_verdict"] for row in feature_rows]
    model = _build_model()
    model.fit(x_values, y_values)

    return {
        "model": model,
        "feature_names": feature_names,
        "labels": LABELS,
    }


def collect_model_feature_names(
    feature_rows: list[dict[str, object]],
) -> tuple[str, ...]:
    if not feature_rows:
        raise ValueError("Cannot collect feature names from empty rows.")

    numeric_features = tuple(
        key
        for key in feature_rows[0]
        if key in _base_numeric_feature_names() or key.startswith("signal_")
    )
    sample_type_features = tuple(f"sample_type_{sample_type}" for sample_type in SAMPLE_TYPES)
    return numeric_features + sample_type_features


def build_feature_matrix(
    feature_rows: list[dict[str, object]],
    feature_names: tuple[str, ...],
) -> list[list[float]]:
    return [
        [_feature_value(row, feature_name) for feature_name in feature_names]
        for row in feature_rows
    ]


def build_prediction_rows(
    evaluation: BaselineEvaluation,
) -> list[dict[str, object]]:
    return [
        {
            "sample_type": prediction.sample_type,
            "sample_id": prediction.sample_id,
            "expected_verdict": prediction.expected_verdict,
            "heuristic_verdict": prediction.heuristic_verdict,
            "baseline_verdict": prediction.baseline_verdict,
            "heuristic_correct": prediction.heuristic_correct,
            "baseline_correct": prediction.baseline_correct,
        }
        for prediction in evaluation.predictions
    ]


def _cross_validated_predictions(
    x_values: list[list[float]],
    expected_labels: list[str],
    folds: int,
) -> list[str]:
    if len(set(expected_labels)) < 2:
        raise ValueError("At least two target labels are required for baseline training.")

    smallest_class_count = min(expected_labels.count(label) for label in set(expected_labels))
    split_count = min(folds, smallest_class_count)
    if split_count < 2:
        raise ValueError("At least two examples per class are required for cross-validation.")

    splitter = StratifiedKFold(
        n_splits=split_count,
        shuffle=True,
        random_state=42,
    )
    return list(
        cross_val_predict(
            _build_model(),
            x_values,
            expected_labels,
            cv=splitter,
        )
    )


def _build_model():
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
            solver="liblinear",
        ),
    )


def _feature_value(row: dict[str, object], feature_name: str) -> float:
    if feature_name.startswith("sample_type_"):
        sample_type = feature_name.removeprefix("sample_type_")
        return float(row["sample_type"] == sample_type)

    value = row[feature_name]
    if isinstance(value, bool):
        return float(value)
    return float(value)


def _base_numeric_feature_names() -> tuple[str, ...]:
    return (
        "risk_score",
        "signal_count",
        "signal_score_total",
        "info_signal_count",
        "low_signal_count",
        "medium_signal_count",
        "high_signal_count",
    )


def _format_accuracy(value: float) -> str:
    return f"{value:.1%}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train and evaluate the experimental baseline classifier.",
    )
    parser.add_argument(
        "--folds",
        type=int,
        default=DEFAULT_FOLDS,
        help="Number of stratified cross-validation folds.",
    )
    parser.add_argument(
        "--predictions-csv",
        type=Path,
        help="Optional path for per-example baseline predictions.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        help="Optional path to persist a model trained on all calibration examples.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    evaluation = evaluate_baseline_classifier(folds=args.folds)

    print(f"Calibration examples: {evaluation.total}")
    print(f"Feature columns: {len(evaluation.feature_names)}")
    print(f"Heuristic accuracy: {_format_accuracy(evaluation.heuristic_accuracy)}")
    print(f"Baseline CV accuracy: {_format_accuracy(evaluation.baseline_accuracy)}")
    print(f"Heuristic misses: {len(evaluation.heuristic_misses)}")
    print(f"Baseline CV misses: {len(evaluation.baseline_misses)}")

    if args.predictions_csv:
        write_rows_csv(build_prediction_rows(evaluation), args.predictions_csv)
        print(f"Wrote baseline predictions: {args.predictions_csv}")

    if args.model_path:
        args.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(fit_baseline_classifier(), args.model_path)
        print(f"Wrote trained baseline model: {args.model_path}")


if __name__ == "__main__":
    main()
