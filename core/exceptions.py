class GatewayError(Exception):
    pass


class AuthenticationError(GatewayError):
    pass


class InvalidSessionError(AuthenticationError):
    pass


class SessionExpiredError(AuthenticationError):
    pass


class SessionRevokedError(AuthenticationError):
    pass


class RequestValidationError(GatewayError):
    pass


class UnsupportedProviderError(GatewayError):
    pass


class ProviderRequestError(GatewayError):
    pass


class PromptSecurityError(GatewayError):
    pass
