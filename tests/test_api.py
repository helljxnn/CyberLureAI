from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


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
