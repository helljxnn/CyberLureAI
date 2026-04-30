from backend.app.services.baseline_classifier import (
    build_feature_matrix,
    build_prediction_rows,
    collect_model_feature_names,
    evaluate_baseline_classifier,
    fit_baseline_classifier,
)
from backend.app.services.calibration import (
    build_feature_rows,
    evaluate_default_calibration,
)


def test_baseline_evaluation_compares_model_with_heuristic() -> None:
    evaluation = evaluate_baseline_classifier()

    assert evaluation.total == 30
    assert evaluation.heuristic_accuracy == 1.0
    assert 0 <= evaluation.baseline_accuracy <= 1
    assert evaluation.baseline_accuracy >= 0.5
    assert len(evaluation.predictions) == evaluation.total
    assert all(prediction.expected_verdict for prediction in evaluation.predictions)


def test_prediction_rows_are_csv_ready() -> None:
    evaluation = evaluate_baseline_classifier()
    rows = build_prediction_rows(evaluation)

    assert len(rows) == evaluation.total
    assert set(rows[0]) == {
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


def test_fit_baseline_classifier_returns_model_bundle() -> None:
    bundle = fit_baseline_classifier()

    assert set(bundle) == {"model", "feature_names", "labels"}
    assert "risk_score" in bundle["feature_names"]
    assert bundle["labels"] == ("likely_safe", "review", "suspicious")
    assert hasattr(bundle["model"], "predict")
