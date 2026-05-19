"""Convert external real-world datasets to CyberLureAI calibration CSV format.

Sources:
  - Phishing URLs: Kaggle taruntiwarihp/phishing-site-urls (URL,Label) + OpenPhish feed
  - SMS Spam: UCI SMS Spam Collection (v1=ham/spam, v2=message)

Output:
  - data/external/url_real.csv   (balanced: phishing + legitimate)
  - data/external/message_real.csv (balanced: spam + ham)
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
EXTERNAL_DIR = DATA_DIR / "external"
PHISHING_CSV = DATA_DIR / "phishing_urls" / "phishing_site_urls.csv"
OPENPHISH_TXT = DATA_DIR / "phishing_urls" / "openphish_feed.txt"
SMS_SPAM_CSV = DATA_DIR / "sms_spam" / "spam.csv"

CALIBRATION_FIELDS = ["sample_id", "input", "expected_verdict", "expected_signal"]
RANDOM_SEED = 42
PHISHING_SAMPLE_SIZE = 400
LEGITIMATE_SAMPLE_SIZE = 400
SPAM_SAMPLE_SIZE = 500
HAM_SAMPLE_SIZE = 500
OPENPHISH_SAMPLE_SIZE = 150

_LABEL_MAP = {
    "bad": "suspicious",
    "good": "likely_safe",
    "spam": "suspicious",
    "ham": "likely_safe",
}


def _clean_text(text: str) -> str:
    return text.strip()


def _normalize_url(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return f"http://{text}"


def _is_valid_url(text: str) -> bool:
    normalized = _normalize_url(text)
    return bool(normalized) and 8 <= len(normalized) <= 2000 and "." in normalized


def _is_valid_message(text: str) -> bool:
    return bool(text) and len(text) >= 5


def _sample(items: list[str], label: str, size: int) -> list[tuple[str, str]]:
    sampled = random.sample(items, min(size, len(items)))
    return [(url, label) for url in sampled]


def convert_phishing_urls() -> None:
    print("=== Converting phishing URLs ===")

    bad_urls: list[str] = []
    good_urls: list[str] = []

    print(f"Loading {PHISHING_CSV.name} ...")
    with PHISHING_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            url = _normalize_url(row.get("URL", ""))
            label = _clean_text(row.get("Label", ""))
            mapped = _LABEL_MAP.get(label)
            if not mapped or not url or not _is_valid_url(url):
                continue
            if mapped == "suspicious":
                bad_urls.append(url)
            else:
                good_urls.append(url)
            if len(bad_urls) >= 10000 and len(good_urls) >= 10000:
                break

    print(f"  bad (phishing):  {len(bad_urls):,}")
    print(f"  good (legitimate): {len(good_urls):,}")

    pairs: list[tuple[str, str]] = []
    pairs.extend(_sample(bad_urls, "suspicious", PHISHING_SAMPLE_SIZE))
    pairs.extend(_sample(good_urls, "likely_safe", LEGITIMATE_SAMPLE_SIZE))

    # OpenPhish feed - all phishing
    print(f"Loading {OPENPHISH_TXT.name} ...")
    with OPENPHISH_TXT.open(encoding="utf-8") as f:
        openphish_urls = [_normalize_url(line) for line in f if line.strip() and line.strip().startswith("http")]
    print(f"  openphish URLs: {len(openphish_urls):,}")

    pairs.extend(_sample(openphish_urls, "suspicious", OPENPHISH_SAMPLE_SIZE))

    random.shuffle(pairs)

    out_path = _write_calibration_csv("url", pairs)
    print(f"Wrote {len(pairs):,} URL examples -> {out_path}\n")


def convert_sms_spam() -> None:
    print("=== Converting SMS spam ===")

    spam_msgs: list[str] = []
    ham_msgs: list[str] = []

    print(f"Loading {SMS_SPAM_CSV.name} ...")
    with SMS_SPAM_CSV.open(newline="", encoding="latin-1") as f:
        for row in csv.DictReader(f):
            label_str = _clean_text(row.get("v1", ""))
            message = _clean_text(row.get("v2", ""))
            mapped = _LABEL_MAP.get(label_str)
            if not mapped or not message or not _is_valid_message(message):
                continue
            if mapped == "suspicious":
                spam_msgs.append(message)
            else:
                ham_msgs.append(message)

    print(f"  spam: {len(spam_msgs):,}")
    print(f"  ham:  {len(ham_msgs):,}")

    pairs: list[tuple[str, str]] = []
    pairs.extend(_sample(spam_msgs, "suspicious", SPAM_SAMPLE_SIZE))
    pairs.extend(_sample(ham_msgs, "likely_safe", HAM_SAMPLE_SIZE))
    random.shuffle(pairs)

    out_path = _write_calibration_csv("message", pairs)
    print(f"Wrote {len(pairs):,} message examples -> {out_path}\n")


def _write_calibration_csv(
    sample_type: str,
    pairs: list[tuple[str, str]],
) -> Path:
    prefix = "url" if sample_type == "url" else "sms"
    rows = [
        {
            "sample_id": f"{prefix}_{'phish' if verdict == 'suspicious' else 'safe'}_{i:04d}",
            "input": text,
            "expected_verdict": verdict,
            "expected_signal": "",
        }
        for i, (text, verdict) in enumerate(pairs)
    ]

    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EXTERNAL_DIR / f"{sample_type}_real.csv"

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CALIBRATION_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return out_path


def main() -> None:
    random.seed(RANDOM_SEED)
    convert_phishing_urls()
    convert_sms_spam()
    print("Done. External calibration CSVs ready in data/external/")


if __name__ == "__main__":
    main()
