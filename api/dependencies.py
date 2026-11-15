from __future__ import annotations

from fastapi import Header, HTTPException, Request, status

from auth.authentication import ClientAuthenticationService
from auth.session_manager import SessionManager
from core.exceptions import AuthenticationError, InvalidSessionError


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "INVALID_SESSION", "message": "The session is invalid or expired."})
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "INVALID_SESSION", "message": "The session is invalid or expired."})
    return token


def get_authenticated_session(
    request: Request,
    authorization: str | None = Header(default=None),
    x_session_id: str | None = Header(default=None, alias="X-Session-ID"),
):
    if x_session_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "INVALID_SESSION", "message": "The session is invalid or expired."})

    session_manager: SessionManager = request.app.state.session_manager
    token = get_bearer_token(authorization)
    try:
        session = session_manager.validate_session(x_session_id, token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "INVALID_SESSION", "message": str(exc)}) from exc

    return session
