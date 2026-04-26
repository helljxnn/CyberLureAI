import csv
from pathlib import Path

import pytest

from backend.app.services.message_analyzer import analyze_message
from backend.app.services.url_analyzer import analyze_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
URL_SAMPLES = PROJECT_ROOT / "data" / "examples" / "url_samples.csv"
MESSAGE_SAMPLES = PROJECT_ROOT / "data" / "examples" / "message_samples.csv"


def _load_samples(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as sample_file:
        return list(csv.DictReader(sample_file))


@pytest.mark.parametrize("sample", _load_samples(URL_SAMPLES), ids=lambda row: row["sample_id"])
def test_labeled_url_samples_match_expected_verdict(sample: dict[str, str]) -> None:
    result = analyze_url(sample["input"])
    signal_codes = {signal.code for signal in result.signals}

    assert result.verdict == sample["expected_verdict"]
    assert sample["expected_signal"] in signal_codes


@pytest.mark.parametrize("sample", _load_samples(MESSAGE_SAMPLES), ids=lambda row: row["sample_id"])
def test_labeled_message_samples_match_expected_verdict(sample: dict[str, str]) -> None:
    result = analyze_message(sample["input"])
    signal_codes = {signal.code for signal in result.signals}

    assert result.verdict == sample["expected_verdict"]
    assert sample["expected_signal"] in signal_codes
