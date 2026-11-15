# Secure AI Gateway — Implementation Plan

## 1. Project Overview

### Objective

Build a lightweight Python-based AI Security Gateway that acts as an intermediary between an AI Agent Server and external LLM providers.

The gateway must inspect incoming prompts, identify sensitive information, sanitize the prompt according to configurable security policies, and forward only approved sanitized prompts to the configured LLM provider.

The implementation must prioritize:

- Simplicity and readability.
- Clear separation of responsibilities.
- Loose coupling between modules.
- Single-purpose classes and functions.
- Minimal dependencies.
- Secure-by-default behavior.
- Easy addition of new LLM providers.
- Consistent request and response formats.

### Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| Web framework | FastAPI |
| Request validation | Pydantic |
| HTTP client | HTTPX |
| Configuration | Pydantic Settings |
| Authentication | API credentials + opaque session tokens |
| Initial persistence | In-memory / SQLite |
| External LLM | Hugging Face Inference API |
| Testing | Pytest |
| Logging | Python logging |

Use maintained, compatible library versions and pin dependencies.

---

# 2. High-Level Architecture

```text
                  AI AGENT SERVER
                         |
                         |
                  HTTPS POST Request
                         |
                         v
              +----------------------+
              |  AI SECURITY GATEWAY |
              +----------------------+
                         |
                         v
              +----------------------+
              | Authentication       |
              | & Session Validation |
              +----------------------+
                         |
                         v
              +----------------------+
              | Request Validation   |
              +----------------------+
                         |
                         v
              +----------------------+
              | Prompt Sanitization  |
              |                      |
              | Sensitive Detection  |
              | Risk Calculation     |
              | Placeholder Mapping |
              +----------------------+
                         |
                  Risk Evaluation
                         |
                +--------+--------+
                |                 |
             REJECT             APPROVE
                |                 |
                v                 v
          Error Response    Provider Interface
                                  |
                                  v
                         HuggingFaceProvider
                                  |
                                  v
                         Hugging Face API
                                  |
                                  v
                         LLM Response
                                  |
                                  v
                         Response Validation
                                  |
                                  v
                         AI Agent Server
```

The gateway must not expose its master keys, provider API credentials, or original sensitive-value mappings to the external LLM.

The gateway is a trusted processing boundary. The LLM provider receives the sanitized prompt, not the original prompt.

---

# 3. Project Directory Structure

Use the following modular structure.

```text
secure-ai-gateway/
│
├── auth/
│   ├── __init__.py
│   ├── authentication.py
│   ├── session_manager.py
│   └── token_manager.py
│
├── configuration/
│   ├── __init__.py
│   ├── settings.py
│   └── constants.py
│
├── connection/
│   ├── __init__.py
│   ├── http_client.py
│   └── connection_manager.py
│
├── core/
│   ├── __init__.py
│   ├── gateway.py
│   ├── request_processor.py
│   ├── response_processor.py
│   └── exceptions.py
│
├── persistence/
│   ├── __init__.py
│   ├── session_repository.py
│   └── audit_repository.py
│
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── authentication.py
│   │   └── inference.py
│   └── dependencies.py
│
├── schemas/
│   ├── __init__.py
│   ├── auth_schema.py
│   ├── request_schema.py
│   └── response_schema.py
│
├── sanitization/
│   ├── __init__.py
│   ├── sanitizer.py
│   ├── sensitive_detector.py
│   ├── risk_evaluator.py
│   ├── placeholder_manager.py
│   └── detection_rules.py
│
├── providers/
│   ├── __init__.py
│   ├── base_provider.py
│   ├── huggingface_provider.py
│   └── provider_factory.py
│
├── security/
│   ├── __init__.py
│   ├── encryption.py
│   ├── secure_random.py
│   └── secure_compare.py
│
├── tests/
│   ├── test_authentication.py
│   ├── test_session_manager.py
│   ├── test_sanitizer.py
│   ├── test_risk_evaluator.py
│   ├── test_huggingface_provider.py
│   └── test_gateway.py
│
├── main.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 3.1 Responsibility of each directory

### auth/

Responsible for authenticating the AI Agent Server and managing its sessions.

- `authentication.py`: Validate client credentials.
- `session_manager.py`: Create, validate and expire sessions.
- `token_manager.py`: Generate and validate cryptographically random session tokens.

Authentication and session management must not depend on LLM providers or sanitization logic.

### configuration/

Responsible for application configuration.

- `settings.py`: Load environment variables and application settings.
- `constants.py`: Define application-wide constants and enums.

Never hardcode provider credentials, authentication secrets or encryption keys.

### connection/

Responsible for managing outbound HTTP connections.

- `http_client.py`: Create and configure HTTPX clients.
- `connection_manager.py`: Manage provider connection lifecycle and timeouts.

Do not implement provider-specific request construction here.

### core/

Contains the main gateway orchestration logic.

- `gateway.py`: Main entry point for processing an inference request.
- `request_processor.py`: Coordinate request validation and preprocessing.
- `response_processor.py`: Validate and prepare provider responses.
- `exceptions.py`: Define application-specific exceptions.

The core layer coordinates components. It should not contain provider-specific implementation or cryptographic algorithms.

### persistence/

Responsible for storing application state.

- `session_repository.py`: Store and retrieve session information.
- `audit_repository.py`: Store security events and request metadata.

Do not persist original plaintext prompts or sensitive-value mappings by default.

Use an in-memory repository for the initial implementation, with SQLite as an optional persistent implementation.

### api/

Contains HTTP endpoints and API dependencies.

- `routes/authentication.py`: Session creation endpoint.
- `routes/inference.py`: AI inference endpoint.
- `dependencies.py`: Authentication and session validation dependencies.

HTTP routes should remain thin. They must delegate actual processing to the core layer.

### schemas/

Contains Pydantic request and response models.

- `auth_schema.py`: Authentication and session schemas.
- `request_schema.py`: Inference request schemas.
- `response_schema.py`: Standard response and error schemas.

### sanitization/

Responsible for identifying and removing or replacing sensitive information.

- `sanitizer.py`: Main sanitization interface.
- `sensitive_detector.py`: Identify sensitive information.
- `risk_evaluator.py`: Calculate risk based on detected information.
- `placeholder_manager.py`: Replace sensitive values with placeholders.
- `detection_rules.py`: Define detection patterns and sensitive categories.

The sanitization module must not know anything about HTTP requests or external LLM providers.

### providers/

Responsible for external LLM integration.

- `base_provider.py`: Abstract provider interface.
- `huggingface_provider.py`: Hugging Face implementation.
- `provider_factory.py`: Select and instantiate the appropriate provider.

New providers should be added without modifying the gateway orchestration logic.

### security/

Contains reusable cryptographic and security utilities.

- `encryption.py`: Authenticated encryption and decryption utilities where required.
- `secure_random.py`: Generate cryptographically secure random values.
- `secure_compare.py`: Constant-time comparison of secret tokens.

Use established cryptographic libraries. Do not implement custom encryption algorithms.

---

# 4. Authentication and Session Management

Authentication and session management are two separate responsibilities.

## 4.1 Authentication flow

The AI Agent Server must authenticate with the gateway before submitting inference requests.

For the initial implementation, use client ID and client secret authentication over HTTPS.

### Endpoint

`POST /api/v1/auth/sessions`

### Request

```json
{
  "client_id": "agent-server-01",
  "client_secret": "CLIENT_SECRET"
}
```

### Successful response

HTTP 201 Created

```json
{
  "success": true,
  "data": {
    "session_id": "sess_a81f92",
    "session_token": "RANDOM_SECURE_TOKEN",
    "expires_in": 1800
  },
  "error": null
}
```

The gateway must:

1. Validate the client ID.
2. Verify the client secret.
3. Generate a cryptographically secure session token.
4. Store the hash of the session token rather than the raw token.
5. Associate the session with the authenticated client.
6. Set an expiration time.
7. Return the session token to the AI Agent Server.

The token must have sufficient entropy and must never be logged.

## 4.2 Session validation

Every inference request must include:

```http
Authorization: Bearer RANDOM_SECURE_TOKEN
X-Session-ID: sess_a81f92
```

The gateway must verify:

- Session exists.
- Session belongs to the authenticated client.
- Session token is valid.
- Session has not expired.
- Session has not been revoked.

Reject unauthorized requests before processing the prompt.

For the initial implementation, session state can be maintained in memory. SQLite or Redis can be introduced later.

Do not implement a new cryptographic handshake for every request. HTTPS protects each connection, while the application session establishes the authenticated client context.

---

# 5. Inference Request Format

The AI Agent Server will send one POST request for each inference operation.

### Endpoint

`POST /api/v1/inference`

### Headers

```http
Content-Type: application/json
Authorization: Bearer RANDOM_SECURE_TOKEN
X-Session-ID: sess_a81f92
X-Request-ID: req_001
```

### Request body

```json
{
  "model_provider_details": {
    "provider": "huggingface",
    "model": "MODEL_IDENTIFIER"
  },
  "prompt": "Analyze this server configuration. Internal server IP is 10.10.20.30 and database password is SECRET123.",
  "options": {
    "temperature": 0.2,
    "max_tokens": 500
  }
}
```

### Important design rules

1. Provider selection must be validated against supported providers.
2. Model identifiers must be validated against an allowlist or provider configuration.
3. Provider API keys must never be accepted from the AI Agent Server.
4. Arbitrary provider URLs must not be accepted from requests.
5. Request size must be limited.
6. Prompt must be validated before sanitization.
7. Unsupported request fields must be rejected or explicitly handled.

The gateway owns provider credentials and provider configuration.

---

# 6. Prompt Sanitization Engine

This is the most important security component of the application.

The gateway must identify sensitive information and decide whether the prompt can be safely forwarded.

## 6.1 Sensitive information detection

Initially support these categories:

| Category | Example |
|---|---|
| IPv4 addresses | 192.168.1.10 |
| Email addresses | user@example.com |
| API keys | API_KEY_123 |
| Passwords | password=secret123 |
| Access tokens | Bearer eyJ... |
| Private keys | PEM private key blocks |
| Phone numbers | Configurable country formats |
| Credit card numbers | Common card number patterns |

Use separate detection rules for each category.

Use regular expressions for recognizable formats and dedicated validators where appropriate.

Do not assume regex can reliably identify every secret or sensitive value.

## 6.2 Sanitization process

Original prompt:

```text
Analyze the configuration.

Server IP: 192.168.1.10
Username: admin
Password: SECRET123
```

Sanitized prompt:

```text
Analyze the configuration.

Server IP: <INTERNAL_IP_1>
Username: <USERNAME_1>
Password: <SECRET_1>
```

The original-to-placeholder mapping must remain local to the gateway.

Example internal mapping:

```python
{
    "<INTERNAL_IP_1>": "192.168.1.10",
    "<USERNAME_1>": "admin",
    "<SECRET_1>": "SECRET123"
}
```

The mapping must never be sent to the LLM provider.

Prefer request-scoped in-memory mappings and discard them when processing finishes unless an explicitly authorized feature requires otherwise.

## 6.3 Risk evaluation and threshold

The sanitizer must return:

- Sanitized prompt.
- Detected sensitive categories.
- Detection count.
- Risk score.
- Decision.

Define a configurable risk policy.

For example:

| Detection | Example weight |
|---|---:|
| Internal IP address | 10 |
| Email address | 10 |
| Username | 10 |
| Phone number | 15 |
| Password | 40 |
| API key | 50 |
| Private key | 100 |

These weights are initial policy examples, not mathematically validated security scores.

Calculate:

```text
risk_score = sum(weights of detected categories)
```

Use configurable thresholds:

```text
0 - 29: APPROVE
30 - 59: APPROVE_WITH_SANITIZATION
60 - 100+: REJECT
```

Additionally, define mandatory rejection rules.

For example:

- Private keys must always cause rejection.
- Certain high-confidence credential detections must always cause rejection.
- Sanitization failure must cause rejection.
- Unknown detector errors must fail closed.

The threshold must not be treated as proof that the remaining prompt is safe. It is a configurable policy decision.

## 6.4 Sanitization result format

Internal result:

```python
SanitizationResult(
    sanitized_prompt="Analyze the configuration. Server IP: <INTERNAL_IP_1>",
    detected_categories=["INTERNAL_IP"],
    detection_count=1,
    risk_score=10,
    decision="APPROVE"
)
```

Create a dedicated result schema.

The gateway should not expose the original sensitive values in its API response or logs.

---

# 7. LLM Provider Abstraction

The gateway must support multiple providers without changing the core processing logic.

## 7.1 Base provider interface

File: `providers/base_provider.py`

Define an abstract class with one main operation:

```python
from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        options: dict
    ) -> str:
        """Generate a response from the selected LLM."""
        pass
```

All providers must implement this interface.

## 7.2 Hugging Face provider

File: `providers/huggingface_provider.py`

Responsibilities:

1. Accept sanitized prompt.
2. Validate model configuration.
3. Retrieve provider credentials from gateway configuration.
4. Build the Hugging Face request.
5. Send the request using HTTPX.
6. Handle provider errors.
7. Extract the generated text.
8. Return a normalized response.

Example:

```python
class HuggingFaceProvider(BaseProvider):

    async def generate(self, prompt, model, options):
        # Send the sanitized prompt to Hugging Face.
        # Validate the response.
        # Return generated text.
        pass
```

Use the currently supported Hugging Face inference endpoint and response format for the selected model.

Do not assume every Hugging Face model supports the same task or request schema.

## 7.3 Provider factory

File: `providers/provider_factory.py`

Responsibilities:

- Read provider name.
- Return the correct provider implementation.
- Reject unsupported providers.

Example:

```python
def get_provider(provider_name: str) -> BaseProvider:

    if provider_name == "huggingface":
        return HuggingFaceProvider()

    raise UnsupportedProviderError()
```

The gateway must depend on `BaseProvider`, not directly on `HuggingFaceProvider`.

Later, adding an OpenAI or Gemini implementation should require only a new provider class and factory registration.

---

# 8. Complete Gateway Processing Flow

The gateway must process each inference request synchronously.

Do not introduce queues, background workers or message brokers in the initial implementation.

### Processing sequence

**Step 1: Receive request**

AI Agent Server calls:

`POST /api/v1/inference`

**Step 2: Authenticate request**

Validate bearer token and session ID.

If authentication fails, return HTTP 401 or 403.

**Step 3: Validate request**

Validate provider, model, prompt and generation options using Pydantic.

**Step 4: Sanitize prompt**

Pass the original prompt to the sanitization engine.

**Step 5: Evaluate risk**

Calculate the risk score and evaluate mandatory rejection rules.

**Step 6: Decide**

If rejected, stop processing and return a security rejection response.

If approved, continue.

**Step 7: Select provider**

Use the provider factory to obtain the selected provider.

**Step 8: Invoke LLM**

Send only the sanitized prompt to the external provider.

**Step 9: Process response**

Validate the provider response and optionally scan it for sensitive information before returning it.

Do not blindly restore original placeholders in the model response. Any restoration feature must be explicitly authorized and validated.

**Step 10: Return response**

Return a normalized response to the AI Agent Server.

The original request should result in one synchronous HTTP response. Do not implement an additional polling mechanism.

---

# 9. API Response Formats

All responses must use a consistent envelope.

## 9.1 Successful response

HTTP 200 OK

```json
{
  "success": true,
  "data": {
    "request_id": "req_001",
    "provider": "huggingface",
    "model": "MODEL_IDENTIFIER",
    "content": "The configuration contains an internal server address and should be reviewed for security.",
    "security": {
      "sanitized": true,
      "risk_score": 10,
      "detected_categories": [
        "INTERNAL_IP"
      ]
    }
  },
  "error": null
}
```

Do not return the original prompt or sensitive-value mapping.

## 9.2 Security rejection response

HTTP 422 Unprocessable Entity

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PROMPT_SECURITY_REJECTED",
    "message": "The prompt contains sensitive information that violates the configured security policy.",
    "details": {
      "risk_score": 100,
      "detected_categories": [
        "PRIVATE_KEY"
      ]
    }
  }
}
```

Do not include the detected secret values in the response.

## 9.3 Authentication failure

HTTP 401 Unauthorized

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_SESSION",
    "message": "The session is invalid or expired."
  }
}
```

## 9.4 Unsupported provider

HTTP 400 Bad Request

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNSUPPORTED_PROVIDER",
    "message": "The requested provider is not supported."
  }
}
```

## 9.5 External provider failure

HTTP 502 Bad Gateway

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PROVIDER_REQUEST_FAILED",
    "message": "The external AI provider could not process the request."
  }
}
```

## 9.6 Provider timeout

HTTP 504 Gateway Timeout

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PROVIDER_TIMEOUT",
    "message": "The external AI provider did not respond within the configured timeout."
  }
}
```

## 9.7 Request validation failure

HTTP 422 Unprocessable Entity

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request contains invalid or missing fields."
  }
}
```

All error responses must be sanitized. Never expose internal exceptions, stack traces, provider credentials or sensitive prompt contents.

---

# 10. Main Orchestration Responsibility

File: `core/gateway.py`

This should be the main coordinator of the entire inference workflow.

It should not implement authentication, sanitization or provider communication itself.

Conceptual implementation:

```python
class SecureAIGateway:

    def __init__(
        self,
        sanitizer,
        provider_factory,
        response_processor
    ):
        self.sanitizer = sanitizer
        self.provider_factory = provider_factory
        self.response_processor = response_processor

    async def process_request(self, request):

        # Sanitize and evaluate the incoming prompt.
        result = self.sanitizer.sanitize(request.prompt)

        # Reject prompts that violate security policy.
        if result.decision == "REJECT":
            raise PromptSecurityError()

        # Select the configured provider.
        provider = self.provider_factory.get_provider(
            request.model_provider_details.provider
        )

        # Generate a response using sanitized information.
        content = await provider.generate(
            prompt=result.sanitized_prompt,
            model=request.model_provider_details.model,
            options=request.options
        )

        # Validate the provider response.
        return self.response_processor.process(content, result)
```

This is conceptual pseudocode. Adapt the factory, schemas and exception handling to the final implementation.

Keep the orchestration readable. Avoid excessive abstractions and unnecessary inheritance.

---

# 11. Security Requirements

These requirements are mandatory.

## Transport security

- Use HTTPS/TLS for agent-to-gateway communication.
- Use HTTPS/TLS for gateway-to-provider communication.
- Do not expose the service over an unsecured network interface in production.

## Authentication

- Never store client secrets in source code.
- Store only hashes of opaque session tokens.
- Enforce session expiration.
- Support session revocation.
- Prevent token leakage through logs.

## Prompt security

- Apply a maximum request size.
- Sanitize before external transmission.
- Never send the original prompt to the provider.
- Never send the placeholder mapping to the provider.
- Reject on sanitizer failure.
- Do not trust model-generated instructions or output.

## Provider security

- Keep provider API credentials in gateway-side configuration or a secret manager.
- Do not accept arbitrary provider endpoints from users.
- Validate provider and model selections.
- Configure request timeouts.
- Limit response size.
- Do not log provider authorization headers.

## Logging

Log:

- Request ID.
- Client ID.
- Session ID (non-secret identifier).
- Provider name.
- Model name.
- Request duration.
- Sanitization decision.
- Risk score.
- Error code.

Never log:

- Original prompt.
- Plaintext secrets.
- Session tokens.
- Provider API keys.
- Encryption keys.
- Sensitive-value mappings.

## Resource protection

- Configure request and response size limits.
- Apply per-client rate limiting.
- Limit concurrent provider requests.
- Set provider connection and read timeouts.
- Restrict supported models.
- Avoid unbounded retries.

---

# 12. Testing Requirements

Create unit tests and integration tests.

### Authentication tests

- Valid client credentials.
- Invalid client credentials.
- Expired session.
- Revoked session.
- Invalid session token.
- Session belonging to another client.

### Sanitization tests

- Normal prompt without sensitive information.
- Prompt containing IPv4 addresses.
- Prompt containing email addresses.
- Prompt containing API keys.
- Prompt containing passwords.
- Prompt containing multiple sensitive categories.
- Prompt containing private keys.
- Prompt exceeding the risk threshold.
- Sanitizer failure.
- False-positive detection.

### Provider tests

- Successful Hugging Face response.
- Invalid API credentials.
- Provider timeout.
- Invalid response format.
- Unsupported model.
- Provider unavailable.

Mock external API calls in unit tests.

### Gateway integration tests

- Complete successful inference.
- Rejection due to high-risk input.
- Authentication failure.
- Unsupported provider.
- External provider failure.
- Verify that the original prompt never reaches the provider.
- Verify that the placeholder mapping never reaches the provider.
- Verify that no secret is written to logs.

---

# 13. Implementation Phases

Implement the project incrementally.

### Phase 1 — Application foundation

- Create the directory structure.
- Set up FastAPI.
- Implement configuration loading.
- Implement standard response schemas.
- Create health endpoint.

Deliverable: Application starts successfully.

### Phase 2 — Authentication and sessions

- Implement client authentication.
- Implement session creation.
- Implement session validation.
- Implement session expiration.
- Add authentication dependencies.

Deliverable: Only authenticated AI Agent Servers can access inference endpoints.

### Phase 3 — Sanitization engine

- Implement sensitive detection.
- Implement placeholder replacement.
- Implement risk calculation.
- Implement configurable security thresholds.
- Implement rejection rules.

Deliverable: Original prompts can be inspected and safely transformed according to policy.

### Phase 4 — Provider integration

- Implement BaseProvider.
- Implement HuggingFaceProvider.
- Implement ProviderFactory.
- Configure provider credentials.
- Implement HTTPX communication.

Deliverable: Sanitized prompts can be processed by Hugging Face.

### Phase 5 — Gateway orchestration

- Implement request processing.
- Integrate authentication and sessions.
- Integrate sanitization.
- Integrate provider selection.
- Implement response processing.
- Implement centralized exception handling.

Deliverable: Complete synchronous AI inference workflow.

### Phase 6 — Security testing

- Test authentication.
- Test sanitization.
- Test provider failures.
- Test prompt leakage.
- Test logging.
- Test request tampering and replay handling.
- Measure performance.

Deliverable: Security-tested gateway.

### Phase 7 — Demonstration

Build a simple interface or TUI that demonstrates:

1. Session authentication.
2. Original prompt submission.
3. Detected sensitive information.
4. Sanitized prompt.
5. Risk evaluation.
6. External LLM request.
7. Generated response.
8. Security rejection scenarios.

---

# 14. Coding Standards and Design Principles

Follow these principles throughout the implementation.

1. **Single Responsibility:** Every class and function must have one clear responsibility.
2. **Loose Coupling:** Components should communicate through interfaces and clearly defined data structures.
3. **Dependency Injection:** Inject providers, sanitizers and repositories rather than creating them throughout the application.
4. **Explicit Error Handling:** Use application-specific exceptions and centralized HTTP exception handling.
5. **Type Safety:** Use Python type hints and Pydantic schemas.
6. **Minimal Abstraction:** Do not create interfaces for components that have only one implementation unless there is a genuine extension or testing requirement.
7. **Configuration Separation:** Keep environment-specific values outside the source code.
8. **No Business Logic in Routes:** API routes should only validate, delegate and return responses.
9. **No Sensitive Logging:** Never log original prompts or credentials.
10. **Readable Code:** Prefer straightforward functions over unnecessary design patterns.

Use concise, meaningful function names and one-line comments only where the purpose is not immediately obvious.

Avoid:
- Deep inheritance hierarchies.
- Global mutable state.
- Circular imports.
- Large service classes.
- Overengineering.
- Custom cryptographic algorithms.
- Unnecessary asynchronous background processing.

---

# 15. Definition of Done

The initial version is complete when all the following conditions are satisfied.

- [ ] AI Agent Server can authenticate with the gateway.
- [ ] Gateway can create and validate sessions.
- [ ] Every inference request requires a valid session.
- [ ] Gateway accepts the defined JSON request format.
- [ ] Sensitive information is detected.
- [ ] Sensitive values are replaced with placeholders.
- [ ] Risk threshold is configurable.
- [ ] High-risk prompts are rejected.
- [ ] Original sensitive data is never forwarded to the external provider.
- [ ] Provider selection works through an abstraction.
- [ ] Hugging Face integration works.
- [ ] Successful responses follow the standard response schema.
- [ ] Errors follow the standard error schema.
- [ ] No sensitive information is exposed in application logs.
- [ ] Provider API credentials remain gateway-side.
- [ ] External API failures and timeouts are handled.
- [ ] Unit and integration tests pass.
- [ ] Complete workflow can be demonstrated.

---

# 16. Instructions for GitHub Copilot

Implement this project strictly according to the architecture and responsibilities defined in this document.

Before writing code:

1. Inspect the existing repository.
2. Understand the existing directory structure.
3. Identify missing modules.
4. Propose the implementation sequence.
5. Do not unnecessarily modify existing files.

During implementation:

- Implement one phase at a time.
- Keep every module independent.
- Follow the defined request and response contracts.
- Use Python type hints.
- Use Pydantic for request and response validation.
- Use dependency injection.
- Keep functions small and readable.
- Avoid unnecessary abstractions.
- Write unit tests alongside each module.
- Never forward the original prompt to an external provider.
- Never expose sensitive-value mappings.
- Never hardcode credentials.
- Never silently bypass sanitization failures.

Do not implement all phases in one large file.

After each phase, verify that the implementation follows the directory responsibilities and passes its corresponding tests.

**Priority: Security correctness > Readability > Maintainability > Performance > Additional features.**

The first implementation should be a working, secure, synchronous AI Security Gateway with Hugging Face integration. Additional providers, advanced cryptographic features, distributed sessions and advanced privacy-preserving inference can be introduced later without redesigning the core architecture.
