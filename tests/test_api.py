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
        json={"url": "http://secure-login-example.com/verify"},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["url"] == "http://secure-login-example.com/verify"
    assert body["risk_level"] in {"low", "medium", "high"}
    assert isinstance(body["risk_score"], int)
    assert "recommended_action" in body
    assert isinstance(body["reasons"], list)
    assert len(body["reasons"]) >= 1


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


def test_url_analysis_endpoint_rejects_invalid_url() -> None:
    response = client.post(
        "/analyze/url",
        json={"url": "not-a-valid-url"},
    )

    assert response.status_code == 422


def test_message_analysis_endpoint_rejects_blank_message() -> None:
    response = client.post(
        "/analyze/message",
        json={"message": "    "},
    )

    assert response.status_code == 422


def test_message_analysis_endpoint_trims_whitespace() -> None:
    response = client.post(
        "/analyze/message",
        json={"message": "   urgent verify your account now   "},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["message"] == "urgent verify your account now"
