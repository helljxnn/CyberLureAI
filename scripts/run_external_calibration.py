"""Quick calibration run on external real-world data."""
from backend.app.services.calibration import evaluate_external_calibration, summarize_calibration_results

results = evaluate_external_calibration()
summary = summarize_calibration_results(results)

print(f"Total ejemplos: {summary['total']}")
print(f"Verdict accuracy: {summary['verdict_accuracy']:.1%}")
print(f"Correct: {summary['verdict_status_counts']['correct']}")
print(f"False positives: {summary['verdict_status_counts']['false_positive']}")
print(f"False negatives: {summary['verdict_status_counts']['false_negative']}")
print(f"Signal match rate: {summary['signal_match_rate']:.1%}")
print()

fn_count = 0
for item in summary["needs_review"]:
    if item["verdict_status"] == "false_negative":
        fn_count += 1

print(f"=== Top 30 False Negatives (phishing/spam missed) out of {fn_count} total ===")
shown = 0
for item in summary["needs_review"]:
    if item["verdict_status"] == "false_negative" and shown < 30:
        input_preview = str(item["input"])[:100]
        signals = str(item.get("actual_signal_codes", ""))[:120]
        print(f"  [{item['sample_type']}] {item['sample_id']}")
        print(f"    expected={item['expected_verdict']}, actual={item['actual_verdict']}, risk_score={item['risk_score']}")
        print(f"    input: {input_preview}")
        print(f"    signals: {signals}")
        shown += 1

print()
print("=== Top 15 False Positives (safe flagged as risky) ===")
shown = 0
for item in summary["needs_review"]:
    if item["verdict_status"] == "false_positive" and shown < 15:
        input_preview = str(item["input"])[:100]
        signals = str(item.get("actual_signal_codes", ""))[:120]
        print(f"  [{item['sample_type']}] {item['sample_id']}")
        print(f"    expected={item['expected_verdict']}, actual={item['actual_verdict']}, risk_score={item['risk_score']}")
        print(f"    input: {input_preview}")
        print(f"    signals: {signals}")
        shown += 1
