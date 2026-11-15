import hmac


def secure_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)
