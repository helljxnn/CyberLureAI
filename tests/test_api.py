from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root_endpoint_returns_api_summary() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "CyberLureAI API",
        "version": "0.1.0",
        "status": "running",
        "environment": "development",
        "docs_url": "/docs",
        "available_endpoints": [
            "/health",
            "/analyze/url",
            "/analyze/message",
        ],
    }


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "CyberLureAI API",
    }


def test_url_analysis_endpoint_returns_expected_shape() -> None:
    response = client.post(
        "/analyze/url",
        json={"url": "http://secure-login-bank-verify.example.com"},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["url"] == "http://secure-login-bank-verify.example.com/"
    assert body["risk_level"] == "high"
    assert body["verdict"] == "suspicious"
    assert body["risk_score"] >= 70
    assert "recommended_action" in body
    assert isinstance(body["reasons"], list)
    assert len(body["reasons"]) >= 2
    assert isinstance(body["signals"], list)
    assert len(body["signals"]) == len(body["reasons"])
    assert {"code", "severity", "score", "description"} <= set(body["signals"][0])
    assert body["experimental_model"]["status"] == "available"
    assert body["experimental_model"]["strategy"] == "separate_by_type"
    assert body["experimental_model"]["sample_type"] == "url"
    assert body["experimental_model"]["verdict"] in {
        "likely_safe",
        "review",
        "suspicious",
    }
    assert isinstance(body["experimental_model"]["agrees_with_heuristic"], bool)


def test_url_analysis_endpoint_flags_ip_address_destination() -> None:
    response = client.post(
        "/analyze/url",
        json={"url": "http://192.168.0.10/secure-login"},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["risk_level"] == "high"
    assert body["verdict"] == "suspicious"
    assert any("IP address" in reason for reason in body["reasons"])
    assert any(signal["code"] == "ip_address_destination" for signal in body["signals"])


def test_message_analysis_endpoint_flags_suspicious_content() -> None:
    response = client.post(
        "/analyze/message",
        json={
            "message": (
                "Urgent: verify your bank account now by clicking "
                "https://fake-bank-alert.example"
            )
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["risk_level"] in {"medium", "high"}
    assert body["verdict"] in {"review", "suspicious"}
    assert isinstance(body["risk_score"], int)
    assert len(body["reasons"]) >= 1
    assert body["experimental_model"]["status"] == "available"
    assert body["experimental_model"]["strategy"] == "separate_by_type"
    assert body["experimental_model"]["sample_type"] == "message"
    assert body["experimental_model"]["verdict"] in {
        "likely_safe",
        "review",
        "suspicious",
    }


def test_message_analysis_endpoint_flags_shortened_link_threat() -> None:
    response = client.post(
        "/analyze/message",
        json={
            "message": (
                "Security alert: your account will be locked today. "
                "Verify now at https://bit.ly/secure-login"
            )
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["risk_level"] == "high"
    assert body["verdict"] == "suspicious"
    assert any("shortened link" in reason.lower() for reason in body["reasons"])
    assert any(signal["code"] == "shortened_link" for signal in body["signals"])


def test_url_analysis_endpoint_rejects_invalid_url() -> None:
    response = client.post(
        "/analyze/url",
        json={"url": "not-a-valid-url"},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "url"


def test_message_analysis_endpoint_rejects_blank_message() -> None:
    response = client.post(
        "/analyze/message",
        json={"message": "    "},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert "non-space characters" in response.json()["details"][0]["message"]


def test_message_analysis_endpoint_trims_whitespace() -> None:
    response = client.post(
        "/analyze/message",
        json={"message": "   urgent verify your account now   "},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["message"] == "urgent verify your account now"
