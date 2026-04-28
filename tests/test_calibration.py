import csv

from backend.app.services.calibration import (
    LabeledExample,
    build_feature_rows,
    collect_signal_codes,
    evaluate_default_calibration,
    evaluate_labeled_examples,
    summarize_calibration_results,
    write_rows_csv,
)


def test_default_calibration_summary_has_no_current_misses() -> None:
    results = evaluate_default_calibration()
    summary = summarize_calibration_results(results)

    assert summary["total"] == len(results)
    assert summary["verdict_matches"] == len(results)
    assert summary["signal_matches"] == len(results)
    assert summary["verdict_status_counts"] == {
        "correct": len(results),
        "false_positive": 0,
        "false_negative": 0,
    }
    assert summary["needs_review"] == []


def test_calibration_tracks_false_positives_and_false_negatives() -> None:
    examples = [
        LabeledExample(
            sample_type="url",
            sample_id="overflagged_url",
            input_value="http://example.com/account",
            expected_verdict="likely_safe",
            expected_signal="no_strong_indicators",
        ),
        LabeledExample(
            sample_type="message",
            sample_id="missed_message",
            input_value="Regular team sync tomorrow.",
            expected_verdict="suspicious",
            expected_signal="urgency_pressure",
        ),
    ]

    results = evaluate_labeled_examples(examples)
    summary = summarize_calibration_results(results)

    assert [result.verdict_status for result in results] == [
        "false_positive",
        "false_negative",
    ]
    assert summary["verdict_status_counts"]["false_positive"] == 1
    assert summary["verdict_status_counts"]["false_negative"] == 1
    assert len(summary["needs_review"]) == 2


def test_feature_rows_include_stable_signal_columns() -> None:
    results = evaluate_default_calibration()
    signal_codes = collect_signal_codes(results)
    rows = build_feature_rows(results, signal_codes)
    rows_by_id = {row["sample_id"]: row for row in rows}

    assert len(rows) == len(results)
    assert all(set(row) == set(rows[0]) for row in rows)
    assert rows_by_id["review_shortener"]["signal_link_shortener"] == 1
    assert rows_by_id["safe_openai"]["signal_no_strong_indicators"] == 1
    assert rows_by_id["suspicious_bank_lockout"]["signal_shortened_link"] == 1
    assert rows_by_id["suspicious_bank_lockout"]["high_signal_count"] >= 1


def test_write_feature_rows_csv(tmp_path) -> None:
    results = evaluate_default_calibration()
    rows = build_feature_rows(results)
    output_path = tmp_path / "features.csv"

    write_rows_csv(rows, output_path)

    with output_path.open(newline="", encoding="utf-8") as output_file:
        written_rows = list(csv.DictReader(output_file))

    assert len(written_rows) == len(rows)
    assert "signal_no_strong_indicators" in written_rows[0]
    assert "risk_score" in written_rows[0]
