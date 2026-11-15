from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from auth.authentication import ClientAuthenticationService, InvalidClientError
from auth.session_manager import SessionManager
from schemas.auth_schema import ClientAuthRequest, SessionResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/sessions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_session(payload: ClientAuthRequest, request: Request) -> dict:
    auth_service: ClientAuthenticationService = request.app.state.auth_service
    session_manager: SessionManager = request.app.state.session_manager

    if not auth_service.validate(payload.client_id, payload.client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CLIENT", "message": "The client credentials are invalid."},
        )

    session = session_manager.create_session(payload.client_id)
    response = {
        "success": True,
        "data": {
            "session_id": session["session_id"],
            "session_token": session["session_token"],
            "expires_in": session["expires_in"],
        },
        "error": None,
    }
    return response
