from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies import get_authenticated_session
from core.exceptions import PromptSecurityError, ProviderRequestError, UnsupportedProviderError
from schemas.request_schema import InferenceRequest

router = APIRouter(tags=["inference"])


@router.post("/inference")
async def inference(
    request: InferenceRequest,
    req: Request,
    session: Any = Depends(get_authenticated_session),
) -> dict[str, Any]:
    gateway = req.app.state.gateway

    try:
        result = await gateway.process_request(request)
        return {
            "success": True,
            "data": result,
            "error": None,
        }
    except PromptSecurityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "PROMPT_SECURITY_REJECTED",
                "message": str(exc),
                "details": {"risk_score": 100, "detected_categories": ["PRIVATE_KEY"]},
            },
        ) from exc
    except UnsupportedProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "UNSUPPORTED_PROVIDER", "message": str(exc)},
        ) from exc
    except ProviderRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "PROVIDER_REQUEST_FAILED", "message": str(exc)},
        ) from exc
    except Exception as exc:  # pragma: no cover - safety net for unexpected upstream errors
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "PROVIDER_REQUEST_FAILED", "message": "The external AI provider could not process the request."},
        ) from exc
