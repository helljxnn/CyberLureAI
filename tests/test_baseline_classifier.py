from backend.app.services.baseline_classifier import (
    build_class_metric_rows,
    build_feature_matrix,
    build_prediction_rows,
    build_sample_type_metric_rows,
    collect_model_feature_names,
    compare_baseline_strategies,
    evaluate_baseline_classifier,
    evaluate_separate_baseline_classifiers,
    fit_baseline_classifier,
    fit_separate_baseline_classifiers,
)
from backend.app.services.calibration import (
    build_feature_rows,
    evaluate_default_calibration,
)


def test_baseline_evaluation_compares_model_with_heuristic() -> None:
    calibration_results = evaluate_default_calibration()
    evaluation = evaluate_baseline_classifier()

    assert evaluation.total == len(calibration_results)
    assert evaluation.heuristic_accuracy == 1.0
    assert 0 <= evaluation.baseline_accuracy <= 1
    assert evaluation.baseline_accuracy >= 0.7
    assert len(evaluation.predictions) == evaluation.total
    assert all(prediction.expected_verdict for prediction in evaluation.predictions)
    assert len(evaluation.class_metrics) == 3
    assert len(evaluation.sample_type_metrics) == 2


def test_prediction_rows_are_csv_ready() -> None:
    evaluation = evaluate_baseline_classifier()
    rows = build_prediction_rows(evaluation)

    assert len(rows) == evaluation.total
    assert set(rows[0]) == {
        "strategy",
        "sample_type",
        "sample_id",
        "expected_verdict",
        "heuristic_verdict",
        "baseline_verdict",
        "heuristic_correct",
        "baseline_correct",
    }


def test_feature_matrix_includes_signal_and_sample_type_columns() -> None:
    results = evaluate_default_calibration()
    rows = build_feature_rows(results)
    feature_names = collect_model_feature_names(rows)
    matrix = build_feature_matrix(rows, feature_names)

    assert "risk_score" in feature_names
    assert "signal_no_strong_indicators" in feature_names
    assert "sample_type_message" in feature_names
    assert "sample_type_url" in feature_names
    assert len(matrix) == len(rows)
    assert all(len(row) == len(feature_names) for row in matrix)


def test_separate_baseline_improves_current_accuracy() -> None:
    unified_evaluation, separate_evaluation = compare_baseline_strategies()

    assert unified_evaluation.strategy == "unified"
    assert separate_evaluation.strategy == "separate_by_type"
    assert separate_evaluation.baseline_accuracy >= unified_evaluation.baseline_accuracy - 0.02
    assert len(separate_evaluation.baseline_misses) <= len(unified_evaluation.baseline_misses) + 3


def test_metric_rows_are_csv_ready() -> None:
    evaluation = evaluate_separate_baseline_classifiers()
    class_rows = build_class_metric_rows(evaluation)
    sample_type_rows = build_sample_type_metric_rows(evaluation)

    assert {row["label"] for row in class_rows} == {"likely_safe", "review", "suspicious"}
    assert {row["sample_type"] for row in sample_type_rows} == {"message", "url"}
    assert all("strategy" in row for row in class_rows)
    assert all("strategy" in row for row in sample_type_rows)


def test_fit_baseline_classifier_returns_model_bundle() -> None:
    bundle = fit_baseline_classifier()

    assert set(bundle) == {"model", "feature_names", "labels", "strategy"}
    assert "risk_score" in bundle["feature_names"]
    assert bundle["labels"] == ("likely_safe", "review", "suspicious")
    assert hasattr(bundle["model"], "predict")
    assert bundle["strategy"] == "unified"


def test_fit_separate_baseline_classifiers_returns_models_by_type() -> None:
    bundle = fit_separate_baseline_classifiers()

    assert set(bundle) == {"models", "feature_names", "labels", "strategy"}
    assert set(bundle["models"]) == {"message", "url"}
    assert bundle["labels"] == ("likely_safe", "review", "suspicious")
    assert bundle["strategy"] == "separate_by_type"
    assert all(hasattr(model, "predict") for model in bundle["models"].values())
