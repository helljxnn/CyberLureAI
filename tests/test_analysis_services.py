from backend.app.services.message_analyzer import analyze_message
from backend.app.services.url_analyzer import analyze_url


def test_url_analyzer_flags_high_risk_patterns() -> None:
    result = analyze_url("http://secure-login-bank-verify.example.com")

    assert result.risk_level in {"medium", "high"}
    assert result.verdict in {"review", "suspicious"}
    assert result.risk_score >= 40
    assert len(result.reasons) >= 2


def test_url_analyzer_marks_simple_https_url_as_low_risk() -> None:
    result = analyze_url("https://www.openai.com")

    assert result.risk_level == "low"
    assert result.verdict == "likely_safe"
    assert result.risk_score < 40
    assert len(result.reasons) >= 1


def test_message_analyzer_flags_social_engineering_message() -> None:
    result = analyze_message(
        "Urgent!!! Verify your account now using this code: 123456"
    )

    assert result.risk_level in {"medium", "high"}
    assert result.verdict in {"review", "suspicious"}
    assert result.risk_score >= 40
    assert any("sensitive information" in reason.lower() for reason in result.reasons)


def test_message_analyzer_marks_plain_message_as_low_risk() -> None:
    result = analyze_message("Hi, just checking in to confirm our meeting tomorrow.")

    assert result.risk_level == "low"
    assert result.verdict == "likely_safe"
    assert result.risk_score < 40
    assert len(result.reasons) >= 1
