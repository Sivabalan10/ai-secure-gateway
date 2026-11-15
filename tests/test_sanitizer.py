from sanitization.sanitizer import Sanitizer


def test_prompt_without_sensitive_data() -> None:
    result = Sanitizer().sanitize("Analyze the application health and deployment status.")
    assert result.decision == "APPROVE"
    assert result.detection_count == 0
    assert result.detected_categories == []


def test_prompt_with_internal_ip_and_password() -> None:
    result = Sanitizer().sanitize("Server IP is 10.10.20.30 and password=SECRET123.")
    assert result.detection_count >= 2
    assert "INTERNAL_IP" in result.detected_categories
    assert "PASSWORD" in result.detected_categories
    assert result.risk_score >= 40
    assert result.decision in {"APPROVE_WITH_SANITIZATION", "REJECT"}


def test_prompt_with_private_key_is_rejected() -> None:
    key = "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----"
    result = Sanitizer().sanitize(f"Deploy secret: {key}")
    assert result.decision == "REJECT"
    assert "PRIVATE_KEY" in result.detected_categories


def test_false_positive_detection_is_limited() -> None:
    result = Sanitizer().sanitize("This is a harmless sentence with no secrets.")
    assert result.detection_count == 0
    assert result.risk_score == 0
