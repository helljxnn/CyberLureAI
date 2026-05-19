"""Analyze calibration gaps to identify heuristic improvements."""
from collections import Counter

from backend.app.services.calibration import evaluate_external_calibration, summarize_calibration_results

results = evaluate_external_calibration()
summary = summarize_calibration_results(results)

print(f"Total: {summary['total']}, Accuracy: {summary['verdict_accuracy']:.1%}")
print(f"Correct: {summary['verdict_status_counts']['correct']}")
print(f"FP: {summary['verdict_status_counts']['false_positive']}")
print(f"FN: {summary['verdict_status_counts']['false_negative']}")
print()

# Analyze FN by risk_level
fn_by_level: Counter = Counter()
fn_by_actual: Counter = Counter()
fn_signals: Counter = Counter()
fn_url_words: Counter = Counter()

for item in summary["needs_review"]:
    if item["verdict_status"] != "false_negative":
        continue
    fn_by_level[item["risk_level"]] += 1
    fn_by_actual[item["actual_verdict"]] += 1

    signals_str = str(item.get("actual_signal_codes", ""))
    for sig in signals_str.split("|"):
        sig = sig.strip()
        if sig:
            fn_signals[sig] += 1

print("=== FN by Risk Level ===")
for level, count in fn_by_level.most_common():
    print(f"  {level}: {count}")

print("\n=== FN by Actual Verdict ===")
for verdict, count in fn_by_actual.most_common():
    print(f"  {verdict}: {count}")

print("\n=== FN Signal Combinations (top 20) ===")
for sig, count in fn_signals.most_common(20):
    print(f"  {sig}: {count}")

# Analyze FP patterns
fp_signals: Counter = Counter()
print("\n=== Top 15 FPs ===")
for item in summary["needs_review"]:
    if item["verdict_status"] != "false_positive":
        continue
    signals_str = str(item.get("actual_signal_codes", ""))
    for sig in signals_str.split("|"):
        sig = sig.strip()
        if sig:
            fp_signals[sig] += 1
    input_preview = str(item["input"])[:80]
    print(f"  [{item['sample_type']}] {item['risk_level']}:{item['risk_score']} signals={signals_str}")
    print(f"    {input_preview}")

print("\n=== FP Signal Combinations (top 15) ===")
for sig, count in fp_signals.most_common(15):
    print(f"  {sig}: {count}")
