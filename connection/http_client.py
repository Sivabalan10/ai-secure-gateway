from __future__ import annotations

import httpx


def create_http_client(timeout_seconds: float = 30.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout_seconds)
