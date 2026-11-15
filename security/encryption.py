from __future__ import annotations

from cryptography.fernet import Fernet


class EncryptionService:
    def __init__(self, key: str | None = None) -> None:
        self._key = key.encode("utf-8") if key else Fernet.generate_key()
        self._fernet = Fernet(self._key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
