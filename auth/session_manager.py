from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from auth.token_manager import TokenManager
from core.exceptions import InvalidSessionError, SessionExpiredError, SessionRevokedError
from persistence.session_repository import InMemorySessionRepository


@dataclass
class SessionRecord:
    session_id: str
    client_id: str
    token_hash: str
    expires_at: float
    revoked: bool = False


class SessionManager:
    def __init__(
        self,
        repository: InMemorySessionRepository,
        token_manager: TokenManager,
        session_ttl_seconds: int = 1800,
    ) -> None:
        self.repository = repository
        self.token_manager = token_manager
        self.session_ttl_seconds = session_ttl_seconds

    def create_session(self, client_id: str) -> dict[str, Any]:
        token = self.token_manager.generate_token()
        session_id = f"sess_{int(time.time() * 1000) % 1000000:06d}"
        expires_at = time.time() + self.session_ttl_seconds
        record = SessionRecord(
            session_id=session_id,
            client_id=client_id,
            token_hash=self.token_manager.hash_token(token),
            expires_at=expires_at,
        )
        self.repository.add(session_id, {
            "session_id": record.session_id,
            "client_id": record.client_id,
            "token_hash": record.token_hash,
            "expires_at": record.expires_at,
            "revoked": record.revoked,
        })
        return {
            "session_id": session_id,
            "session_token": token,
            "expires_in": self.session_ttl_seconds,
        }

    def validate_session(self, session_id: str, token: str) -> SessionRecord:
        record_data = self.repository.get(session_id)
        if record_data is None:
            raise InvalidSessionError("The session does not exist.")

        if record_data.get("revoked"):
            raise SessionRevokedError("The session has been revoked.")

        expires_at = float(record_data["expires_at"])
        if time.time() > expires_at:
            raise SessionExpiredError("The session has expired.")

        expected_hash = record_data["token_hash"]
        if not self.token_manager.validate_token(token, expected_hash):
            raise InvalidSessionError("The session token is invalid.")

        return SessionRecord(
            session_id=session_id,
            client_id=str(record_data["client_id"]),
            token_hash=str(expected_hash),
            expires_at=expires_at,
            revoked=bool(record_data.get("revoked", False)),
        )

    def revoke_session(self, session_id: str) -> None:
        record = self.repository.get(session_id)
        if record is None:
            raise InvalidSessionError("The session does not exist.")
        record["revoked"] = True
