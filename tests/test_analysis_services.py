from backend.app.services.message_analyzer import analyze_message
from backend.app.services.url_analyzer import analyze_url


def test_url_analyzer_flags_high_risk_patterns() -> None:
    result = analyze_url("http://secure-login-bank-verify.example.com")

    assert result.risk_level == "high"
    assert result.verdict == "suspicious"
    assert result.risk_score >= 70
    assert len(result.reasons) >= 2
    assert len(result.signals) == len(result.reasons)


def test_url_analyzer_marks_simple_https_url_as_low_risk() -> None:
    result = analyze_url("https://www.openai.com")

    assert result.risk_level == "low"
    assert result.verdict == "likely_safe"
    assert result.risk_score < 40
    assert len(result.reasons) >= 1
    assert result.signals[0].code == "no_strong_indicators"


def test_url_analyzer_flags_shortened_links_for_review() -> None:
    result = analyze_url("https://bit.ly/account-update")

    assert result.risk_level == "medium"
    assert result.verdict == "review"
    assert result.risk_score >= 40
    assert any("shortener" in reason.lower() for reason in result.reasons)
    assert any(signal.code == "link_shortener" for signal in result.signals)


def test_url_analyzer_flags_ip_address_destinations_as_high_risk() -> None:
    result = analyze_url("http://192.168.0.10/secure-login")

    assert result.risk_level == "high"
    assert result.verdict == "suspicious"
    assert result.risk_score >= 70
    assert any("ip address" in reason.lower() for reason in result.reasons)
    assert any(signal.code == "ip_address_destination" for signal in result.signals)


def test_url_analyzer_flags_brand_impersonation_patterns() -> None:
    result = analyze_url("https://paypal-secure-check.example.com/login")

    assert result.risk_level == "high"
    assert result.verdict == "suspicious"
    assert result.risk_score >= 70
    assert any("known brand" in reason.lower() for reason in result.reasons)
    assert any(signal.code == "brand_impersonation" for signal in result.signals)


def test_message_analyzer_flags_social_engineering_message() -> None:
    result = analyze_message(
        "Urgent!!! Verify your account now using this code: 123456"
    )

    assert result.risk_level in {"medium", "high"}
    assert result.verdict in {"review", "suspicious"}
    assert result.risk_score >= 40
    assert any("sensitive information" in reason.lower() for reason in result.reasons)
    assert any(signal.code == "sensitive_information_request" for signal in result.signals)


def test_message_analyzer_flags_shortened_link_and_account_threat() -> None:
    result = analyze_message(
        "Security alert: your account will be locked today. "
        "Verify now at https://bit.ly/secure-login"
    )

    assert result.risk_level == "high"
    assert result.verdict == "suspicious"
    assert result.risk_score >= 70
    assert any("shortened link" in reason.lower() for reason in result.reasons)
    assert any("account restriction" in reason.lower() for reason in result.reasons)
    assert any(signal.code == "shortened_link" for signal in result.signals)
    assert any(signal.code == "account_restriction_threat" for signal in result.signals)


def test_message_analyzer_marks_plain_message_as_low_risk() -> None:
    result = analyze_message("Hi, just checking in to confirm our meeting tomorrow.")

    assert result.risk_level == "low"
    assert result.verdict == "likely_safe"
    assert result.risk_score < 40
    assert len(result.reasons) >= 1
    assert result.signals[0].code == "no_strong_indicators"
