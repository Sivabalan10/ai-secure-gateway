import hashlib

from security.secure_random import generate_secure_token
from security.secure_compare import secure_compare


class TokenManager:
    def __init__(self, token_length: int = 32) -> None:
        self.token_length = token_length

    def generate_token(self) -> str:
        return generate_secure_token(length=self.token_length)

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def validate_token(self, candidate: str, expected_hash: str) -> bool:
        return secure_compare(self.hash_token(candidate), expected_hash)
