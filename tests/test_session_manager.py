import time

import pytest

from auth.session_manager import SessionManager
from auth.token_manager import TokenManager
from core.exceptions import InvalidSessionError, SessionExpiredError, SessionRevokedError
from persistence.session_repository import InMemorySessionRepository


def test_create_and_validate_session() -> None:
    repo = InMemorySessionRepository()
    manager = SessionManager(repo, TokenManager(), session_ttl_seconds=1800)

    session = manager.create_session("agent-server-01")
    validated = manager.validate_session(session["session_id"], session["session_token"])

    assert validated.client_id == "agent-server-01"
    assert session["expires_in"] == 1800


def test_invalid_session_token() -> None:
    repo = InMemorySessionRepository()
    manager = SessionManager(repo, TokenManager(), session_ttl_seconds=1800)

    session = manager.create_session("agent-server-01")

    with pytest.raises(InvalidSessionError):
        manager.validate_session(session["session_id"], "not-the-right-token")


def test_session_expiration() -> None:
    repo = InMemorySessionRepository()
    manager = SessionManager(repo, TokenManager(), session_ttl_seconds=1)
    session = manager.create_session("agent-server-01")
    repo.add(session["session_id"], {**repo.get(session["session_id"]), "expires_at": time.time() - 5})

    with pytest.raises(SessionExpiredError):
        manager.validate_session(session["session_id"], session["session_token"])


def test_revoked_session() -> None:
    repo = InMemorySessionRepository()
    manager = SessionManager(repo, TokenManager(), session_ttl_seconds=1800)
    session = manager.create_session("agent-server-01")
    manager.revoke_session(session["session_id"])

    with pytest.raises(SessionRevokedError):
        manager.validate_session(session["session_id"], session["session_token"])
