from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
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
UNIFIED_STRATEGY = "unified"
SEPARATE_STRATEGY = "separate_by_type"


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
class ClassMetrics:
    label: str
    precision: float
    recall: float
    f1_score: float
    support: int


@dataclass(frozen=True)
class SampleTypeMetrics:
    sample_type: str
    total: int
    heuristic_accuracy: float
    baseline_accuracy: float


@dataclass(frozen=True)
class BaselineEvaluation:
    strategy: str
    total: int
    feature_names: tuple[str, ...]
    heuristic_accuracy: float
    baseline_accuracy: float
    predictions: tuple[BaselinePrediction, ...]
    class_metrics: tuple[ClassMetrics, ...]
    sample_type_metrics: tuple[SampleTypeMetrics, ...]

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
    return _evaluate_strategy(
        calibration_results,
        strategy=UNIFIED_STRATEGY,
        folds=folds,
    )


def evaluate_separate_baseline_classifiers(
    results: list[CalibrationResult] | None = None,
    folds: int = DEFAULT_FOLDS,
) -> BaselineEvaluation:
    calibration_results = results or evaluate_default_calibration()
    return _evaluate_strategy(
        calibration_results,
        strategy=SEPARATE_STRATEGY,
        folds=folds,
    )


def compare_baseline_strategies(
    results: list[CalibrationResult] | None = None,
    folds: int = DEFAULT_FOLDS,
) -> tuple[BaselineEvaluation, BaselineEvaluation]:
    calibration_results = results or evaluate_default_calibration()
    return (
        _evaluate_strategy(
            calibration_results,
            strategy=UNIFIED_STRATEGY,
            folds=folds,
        ),
        _evaluate_strategy(
            calibration_results,
            strategy=SEPARATE_STRATEGY,
            folds=folds,
        ),
    )


def fit_baseline_classifier(
    results: list[CalibrationResult] | None = None,
) -> dict[str, object]:
    calibration_results = results or evaluate_default_calibration()
    feature_rows = build_feature_rows(calibration_results)
    feature_names = collect_model_feature_names(feature_rows)
    x_values = build_feature_matrix(feature_rows, feature_names)
    y_values = [str(row["expected_verdict"]) for row in feature_rows]
    model = _build_model()
    model.fit(x_values, y_values)

    return {
        "model": model,
        "feature_names": feature_names,
        "labels": LABELS,
        "strategy": UNIFIED_STRATEGY,
    }


def fit_separate_baseline_classifiers(
    results: list[CalibrationResult] | None = None,
) -> dict[str, object]:
    calibration_results = results or evaluate_default_calibration()
    feature_rows = build_feature_rows(calibration_results)
    feature_names = collect_model_feature_names(feature_rows)
    models: dict[str, object] = {}

    for sample_type in SAMPLE_TYPES:
        scoped_rows = [
            row for row in feature_rows if str(row["sample_type"]) == sample_type
        ]
        if not scoped_rows:
            continue
        x_values = build_feature_matrix(scoped_rows, feature_names)
        y_values = [str(row["expected_verdict"]) for row in scoped_rows]
        model = _build_model()
        model.fit(x_values, y_values)
        models[sample_type] = model

    return {
        "models": models,
        "feature_names": feature_names,
        "labels": LABELS,
        "strategy": SEPARATE_STRATEGY,
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
    sample_type_features = tuple(
        f"sample_type_{sample_type}" for sample_type in SAMPLE_TYPES
    )
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
            "strategy": evaluation.strategy,
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


def build_class_metric_rows(
    evaluation: BaselineEvaluation,
) -> list[dict[str, object]]:
    return [
        {
            "strategy": evaluation.strategy,
            "label": metrics.label,
            "precision": metrics.precision,
            "recall": metrics.recall,
            "f1_score": metrics.f1_score,
            "support": metrics.support,
        }
        for metrics in evaluation.class_metrics
    ]


def build_sample_type_metric_rows(
    evaluation: BaselineEvaluation,
) -> list[dict[str, object]]:
    return [
        {
            "strategy": evaluation.strategy,
            "sample_type": metrics.sample_type,
            "total": metrics.total,
            "heuristic_accuracy": metrics.heuristic_accuracy,
            "baseline_accuracy": metrics.baseline_accuracy,
        }
        for metrics in evaluation.sample_type_metrics
    ]


def _evaluate_strategy(
    calibration_results: list[CalibrationResult],
    strategy: str,
    folds: int,
) -> BaselineEvaluation:
    feature_rows = build_feature_rows(calibration_results)
    feature_names = collect_model_feature_names(feature_rows)
    expected_labels = [str(row["expected_verdict"]) for row in feature_rows]
    heuristic_labels = [str(row["actual_verdict"]) for row in feature_rows]
    baseline_labels = _predictions_for_strategy(
        feature_rows,
        feature_names,
        expected_labels,
        folds,
        strategy,
    )

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
        strategy=strategy,
        total=len(feature_rows),
        feature_names=feature_names,
        heuristic_accuracy=accuracy_score(expected_labels, heuristic_labels),
        baseline_accuracy=accuracy_score(expected_labels, baseline_labels),
        predictions=predictions,
        class_metrics=_build_class_metrics(expected_labels, baseline_labels),
        sample_type_metrics=_build_sample_type_metrics(predictions),
    )


def _predictions_for_strategy(
    feature_rows: list[dict[str, object]],
    feature_names: tuple[str, ...],
    expected_labels: list[str],
    folds: int,
    strategy: str,
) -> list[str]:
    if strategy == UNIFIED_STRATEGY:
        x_values = build_feature_matrix(feature_rows, feature_names)
        return _cross_validated_predictions(x_values, expected_labels, folds)

    if strategy == SEPARATE_STRATEGY:
        predictions = [""] * len(feature_rows)
        for sample_type in SAMPLE_TYPES:
            scoped_indices = [
                index
                for index, row in enumerate(feature_rows)
                if str(row["sample_type"]) == sample_type
            ]
            if not scoped_indices:
                continue

            scoped_rows = [feature_rows[index] for index in scoped_indices]
            scoped_labels = [expected_labels[index] for index in scoped_indices]
            scoped_matrix = build_feature_matrix(scoped_rows, feature_names)
            scoped_predictions = _cross_validated_predictions(
                scoped_matrix,
                scoped_labels,
                folds,
            )
            for index, prediction in zip(
                scoped_indices,
                scoped_predictions,
                strict=True,
            ):
                predictions[index] = prediction

        if any(not prediction for prediction in predictions):
            raise ValueError("Missing predictions while evaluating separate baselines.")
        return predictions

    raise ValueError(f"Unknown baseline strategy: {strategy}")


def _build_class_metrics(
    expected_labels: list[str],
    baseline_labels: list[str],
) -> tuple[ClassMetrics, ...]:
    precision_values, recall_values, f1_values, support_values = (
        precision_recall_fscore_support(
            expected_labels,
            baseline_labels,
            labels=list(LABELS),
            zero_division=0,
        )
    )
    return tuple(
        ClassMetrics(
            label=label,
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1_score),
            support=int(support),
        )
        for label, precision, recall, f1_score, support in zip(
            LABELS,
            precision_values,
            recall_values,
            f1_values,
            support_values,
            strict=True,
        )
    )


def _build_sample_type_metrics(
    predictions: tuple[BaselinePrediction, ...],
) -> tuple[SampleTypeMetrics, ...]:
    metrics: list[SampleTypeMetrics] = []
    for sample_type in SAMPLE_TYPES:
        scoped_predictions = [
            prediction
            for prediction in predictions
            if prediction.sample_type == sample_type
        ]
        if not scoped_predictions:
            continue
        metrics.append(
            SampleTypeMetrics(
                sample_type=sample_type,
                total=len(scoped_predictions),
                heuristic_accuracy=sum(
                    prediction.heuristic_correct for prediction in scoped_predictions
                )
                / len(scoped_predictions),
                baseline_accuracy=sum(
                    prediction.baseline_correct for prediction in scoped_predictions
                )
                / len(scoped_predictions),
            )
        )
    return tuple(metrics)


def _cross_validated_predictions(
    x_values: list[list[float]],
    expected_labels: list[str],
    folds: int,
) -> list[str]:
    if len(set(expected_labels)) < 2:
        raise ValueError(
            "At least two target labels are required for baseline training."
        )

    label_counts = Counter(expected_labels)
    smallest_class_count = min(label_counts.values())
    split_count = min(folds, smallest_class_count)
    if split_count < 2:
        raise ValueError(
            "At least two examples per class are required for cross-validation."
        )

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
        "--class-metrics-csv",
        type=Path,
        help="Optional path for per-class precision, recall, and F1 metrics.",
    )
    parser.add_argument(
        "--sample-type-metrics-csv",
        type=Path,
        help="Optional path for per-sample-type accuracy metrics.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        help="Optional path to persist a unified model trained on all calibration examples.",
    )
    parser.add_argument(
        "--separate-model-dir",
        type=Path,
        help="Optional directory to persist one trained model per sample type.",
    )
    return parser


def _print_evaluation(evaluation: BaselineEvaluation) -> None:
    print(f"Strategy: {evaluation.strategy}")
    print(f"Calibration examples: {evaluation.total}")
    print(f"Feature columns: {len(evaluation.feature_names)}")
    print(f"Heuristic accuracy: {_format_accuracy(evaluation.heuristic_accuracy)}")
    print(f"Baseline CV accuracy: {_format_accuracy(evaluation.baseline_accuracy)}")
    print(f"Heuristic misses: {len(evaluation.heuristic_misses)}")
    print(f"Baseline CV misses: {len(evaluation.baseline_misses)}")
    for metrics in evaluation.sample_type_metrics:
        print(
            f"{metrics.sample_type} baseline accuracy: "
            f"{_format_accuracy(metrics.baseline_accuracy)}"
        )
    for metrics in evaluation.class_metrics:
        print(
            f"{metrics.label}: precision={metrics.precision:.3f}, "
            f"recall={metrics.recall:.3f}, f1={metrics.f1_score:.3f}, "
            f"support={metrics.support}"
        )


def main() -> None:
    args = _build_parser().parse_args()
    unified_evaluation, separate_evaluation = compare_baseline_strategies(
        folds=args.folds
    )

    _print_evaluation(unified_evaluation)
    print("---")
    _print_evaluation(separate_evaluation)

    if args.predictions_csv:
        prediction_rows = build_prediction_rows(unified_evaluation)
        prediction_rows.extend(build_prediction_rows(separate_evaluation))
        write_rows_csv(prediction_rows, args.predictions_csv)
        print(f"Wrote baseline predictions: {args.predictions_csv}")

    if args.class_metrics_csv:
        class_rows = build_class_metric_rows(unified_evaluation)
        class_rows.extend(build_class_metric_rows(separate_evaluation))
        write_rows_csv(class_rows, args.class_metrics_csv)
        print(f"Wrote class metrics: {args.class_metrics_csv}")

    if args.sample_type_metrics_csv:
        sample_type_rows = build_sample_type_metric_rows(unified_evaluation)
        sample_type_rows.extend(build_sample_type_metric_rows(separate_evaluation))
        write_rows_csv(sample_type_rows, args.sample_type_metrics_csv)
        print(f"Wrote sample-type metrics: {args.sample_type_metrics_csv}")

    if args.model_path:
        args.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(fit_baseline_classifier(), args.model_path)
        print(f"Wrote trained baseline model: {args.model_path}")

    if args.separate_model_dir:
        args.separate_model_dir.mkdir(parents=True, exist_ok=True)
        bundle = fit_separate_baseline_classifiers()
        for sample_type, model in bundle["models"].items():
            model_path = args.separate_model_dir / f"{sample_type}_baseline_model.joblib"
            joblib.dump(
                {
                    "model": model,
                    "feature_names": bundle["feature_names"],
                    "labels": bundle["labels"],
                    "sample_type": sample_type,
                    "strategy": SEPARATE_STRATEGY,
                },
                model_path,
            )
            print(f"Wrote trained {sample_type} baseline model: {model_path}")


if __name__ == "__main__":
    main()
