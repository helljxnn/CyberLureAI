"""Stress-test calibration: identify heuristic gaps in adversarial examples."""
from pathlib import Path

from backend.app.services.calibration import (
    evaluate_calibration_file,
    summarize_calibration_results,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "examples"

url_path = DATA_DIR / "url_adversarial.csv"
msg_path = DATA_DIR / "message_adversarial.csv"

if not url_path.exists() or not msg_path.exists():
    print("Adversarial CSV files not found. Run add_adversarial_examples.py first.")
    exit(1)

results = []
if url_path.exists():
    results.extend(evaluate_calibration_file(url_path, "url"))
if msg_path.exists():
    results.extend(evaluate_calibration_file(msg_path, "message"))

summary = summarize_calibration_results(results)

print(f"=== Stress Test Results (adversarial examples) ===")
print(f"Total adversarial examples: {summary['total']}")
print(f"Verdict accuracy: {summary['verdict_accuracy']:.1%}")
print(f"Signal match rate: {summary['signal_match_rate']:.1%}")
print(f"Status: {summary['verdict_status_counts']}")
print()

needs_review = summary["needs_review"]
false_negatives = [
    item for item in summary["needs_review"]
    if item["verdict_status"] == "false_negative"
]
false_positives = [
    item for item in summary["needs_review"]
    if item["verdict_status"] == "false_positive"
]

print(f"Confirmed heuristic gaps (false negatives): {len(false_negatives)}")
print(f"False positives: {len(false_positives)}")
print()

if false_negatives:
    print("=== DOCUMENTED GAPS (heuristic cannot detect these yet) ===")
    for item in false_negatives:
        gap_category = "SCORING" if item["actual_verdict"] == "review" else "BLIND_SPOT"
        print(f"  [{gap_category}] {item['sample_id']}: expected={item['expected_verdict']} -> actual={item['actual_verdict']} (score={item['risk_score']})")
        print(f"    input: {str(item.get('input_value', ''))[:130]}")
        print()

# Print summary by category
scoring_gaps = sum(1 for fn in false_negatives if fn["actual_verdict"] == "review")
blind_spots = sum(1 for fn in false_negatives if fn["actual_verdict"] == "likely_safe")

print(f"Gap breakdown:")
print(f"  Scoring gaps (flagged as review but should be suspicious): {scoring_gaps}")
print(f"  Blind spots (missed entirely, flagged as likely_safe): {blind_spots}")
print(f"  False positives: {len(false_positives)}")
print()

print("=== KNOWN LIMITATIONS ===")
print("1. URL keyword obfuscation (hyphen-breaking) - needs fuzzy matching")
print("2. Legitimate platform abuse (Google Forms, redirectors) - needs content analysis")
print("3. Base64/encoded payloads - needs decoding layer")
print("4. Implicit social engineering (friendly tone, BEC, romance scams) - needs NLP/ML")
print("5. Link-only messages without scam keywords - fundamental heuristic limit")
print("6. IDN homoglyph attacks - needs Unicode normalization beyond ASCII")
print("7. Open redirect detection - needs URL parameter analysis")
