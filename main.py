from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.authentication import router as auth_router
from api.routes.inference import router as inference_router
from auth.authentication import ClientAuthenticationService
from auth.session_manager import SessionManager
from auth.token_manager import TokenManager
from configuration.settings import settings
from connection.connection_manager import ConnectionManager
from core.gateway import SecureAIGateway
from core.response_processor import ResponseProcessor
from persistence.audit_repository import InMemoryAuditRepository
from persistence.session_repository import InMemorySessionRepository
from providers.provider_factory import ProviderFactory
from sanitization.sanitizer import Sanitizer


def build_app() -> FastAPI:
    session_repository = InMemorySessionRepository()
    audit_repository = InMemoryAuditRepository()
    auth_service = ClientAuthenticationService(settings.client_credentials)
    token_manager = TokenManager()
    session_manager = SessionManager(
        repository=session_repository,
        token_manager=token_manager,
        session_ttl_seconds=settings.session_ttl_seconds,
    )
    sanitizer = Sanitizer(max_prompt_size=settings.max_prompt_size)
    connection_manager = ConnectionManager(timeout_seconds=settings.provider_timeout_seconds)
    provider_factory = ProviderFactory(settings=settings, connection_manager=connection_manager)
    response_processor = ResponseProcessor()
    gateway = SecureAIGateway(
        sanitizer=sanitizer,
        provider_factory=provider_factory,
        response_processor=response_processor,
    )

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Secure AI Gateway",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.session_manager = session_manager
    app.state.auth_service = auth_service
    app.state.audit_repository = audit_repository
    app.state.gateway = gateway

    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(inference_router, prefix=settings.api_prefix)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app


app = build_app()
