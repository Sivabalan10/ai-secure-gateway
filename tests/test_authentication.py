from auth.authentication import ClientAuthenticationService


def test_valid_client_credentials() -> None:
    service = ClientAuthenticationService({"agent-server-01": "super-secret"})
    assert service.validate("agent-server-01", "super-secret") is True


def test_invalid_client_credentials() -> None:
    service = ClientAuthenticationService({"agent-server-01": "super-secret"})
    assert service.validate("agent-server-01", "wrong") is False
    assert service.validate("missing-client", "secret") is False
