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
            "/analyze/malware",
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


def test_malware_analysis_endpoint_returns_expected_shape() -> None:
    from backend.app.schemas.malware_analysis import MALWARE_FEATURE_EXAMPLE

    response = client.post(
        "/analyze/malware",
        json={"features": MALWARE_FEATURE_EXAMPLE},
    )

    body = response.json()

    assert response.status_code == 200
    assert isinstance(body["is_malware"], bool)
    assert isinstance(body["label"], str)
    assert isinstance(body["confidence"], (int, float))
    assert 0 <= body["confidence"] <= 1
    assert isinstance(body["probabilities"], dict)
    assert "benign" in body["probabilities"]
    assert "malware" in body["probabilities"]
    assert body["risk_level"] in {"low", "medium", "high"}
    assert isinstance(body["risk_score"], int)
    assert body["verdict"] in {"likely_safe", "review", "suspicious"}
    assert isinstance(body["explanation"], str)
    assert isinstance(body["recommended_action"], str)
    assert isinstance(body["reasons"], list)
    assert len(body["reasons"]) == 2
    assert isinstance(body["signals"], list)
    assert len(body["signals"]) == 3
    assert body["experimental_model"] is None


def test_malware_analysis_endpoint_rejects_empty_features() -> None:
    response = client.post(
        "/analyze/malware",
        json={"features": {}},
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body["is_malware"], bool)
    assert body["risk_level"] in {"low", "medium", "high"}
    assert body["verdict"] in {"likely_safe", "review", "suspicious"}
    assert isinstance(body["confidence"], (int, float))
    assert "benign" in body["probabilities"]
    assert "malware" in body["probabilities"]


def test_malware_analysis_endpoint_rejects_invalid_features() -> None:
    response = client.post(
        "/analyze/malware",
        json={"features": "not-a-dict"},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def _build_minimal_pe_bytes() -> bytes:
    import struct

    dos_header = b"MZ" + b"\x00" * 58 + struct.pack("<I", 64)
    pe_sig = b"PE\x00\x00"
    coff_header = struct.pack(
        "<HHIIIHH",
        0x14C,
        1,
        0,
        0,
        0,
        0xE0,
        0x102,
    )
    opt_header = struct.pack("<HBBIIIII", 0x10B, 1, 0, 0x200, 0, 0, 0x1000, 0x1000)
    opt_header += struct.pack("<I", 0x400000)
    opt_header += struct.pack("<II", 0x1000, 0x200)
    opt_header += struct.pack("<HHHHHH", 4, 0, 0, 0, 4, 0)
    opt_header += struct.pack("<III", 0x3000, 0x200, 0)
    opt_header += struct.pack("<HH", 3, 0x8160)
    opt_header += struct.pack("<IIII", 0x100000, 0x1000, 0x100000, 0x1000)
    opt_header += struct.pack("<II", 0, 16)
    opt_header += b"\x00" * (16 * 8)
    section_header = b".text\x00\x00\x00"
    section_header += struct.pack("<IIII", 0x200, 0x1000, 0x200, 0x200)
    section_header += struct.pack("<IIHHI", 0, 0, 0, 0, 0x60000020)
    file_data = dos_header + pe_sig + coff_header + opt_header + section_header
    file_data += b"\x00" * (0x200 - len(file_data))
    file_data += b"\xCC" * 0x200
    return file_data


def test_malware_upload_endpoint_returns_expected_shape() -> None:
    pe_bytes = _build_minimal_pe_bytes()

    response = client.post(
        "/analyze/malware/upload",
        files={"file": ("test.exe", pe_bytes, "application/octet-stream")},
    )

    body = response.json()

    assert response.status_code == 200
    assert isinstance(body["is_malware"], bool)
    assert isinstance(body["label"], str)
    assert isinstance(body["confidence"], (int, float))
    assert 0 <= body["confidence"] <= 1
    assert isinstance(body["probabilities"], dict)
    assert "benign" in body["probabilities"]
    assert "malware" in body["probabilities"]
    assert body["risk_level"] in {"low", "medium", "high"}
    assert isinstance(body["risk_score"], int)
    assert body["verdict"] in {"likely_safe", "review", "suspicious"}
    assert isinstance(body["explanation"], str)
    assert isinstance(body["recommended_action"], str)
    assert isinstance(body["reasons"], list)
    assert isinstance(body["signals"], list)
    assert body["experimental_model"] is None


def test_malware_upload_endpoint_rejects_non_pe_file() -> None:
    response = client.post(
        "/analyze/malware/upload",
        files={"file": ("test.txt", b"not a PE file", "text/plain")},
    )

    assert response.status_code == 400
    assert "Invalid PE file format" in response.json()["detail"]
