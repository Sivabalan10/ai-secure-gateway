from __future__ import annotations

from dataclasses import dataclass


class InvalidClientError(ValueError):
    pass


@dataclass(frozen=True)
class ClientCredentials:
    client_id: str
    client_secret: str


class ClientAuthenticationService:
    def __init__(self, clients: dict[str, str] | None = None) -> None:
        self._clients = dict(clients or {})

    def validate(self, client_id: str, client_secret: str) -> bool:
        stored_secret = self._clients.get(client_id)
        if stored_secret is None:
            return False
        return stored_secret == client_secret

    def is_valid_client(self, client_id: str, client_secret: str) -> bool:
        return self.validate(client_id, client_secret)

    def get_client_secret(self, client_id: str) -> str | None:
        return self._clients.get(client_id)
