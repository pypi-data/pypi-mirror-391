"""
VocaFuse Python SDK - Simple & Magical

Complete SDK for VocaFuse voice API integration with API client.

Usage Patterns:

1. Everything from Main Package:
   from vocafuse import Client, AccessToken, RequestValidator

2. Full API Client Only:
   from vocafuse import Client
   client = Client(api_key, api_secret)

3. Specific Functionality (Alternative):
   from vocafuse.jwt.access_token import AccessToken
   from vocafuse.webhook.request_validator import RequestValidator
"""

# Main client class
from .client import Client

# JWT token generation
from .jwt.access_token import AccessToken

# Webhook validation
from .webhook.request_validator import RequestValidator

# Exceptions for error handling
from .exceptions import (
    VocaFuseError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServerError,
    RecordingNotFoundError,
    WebhookNotFoundError,
    TranscriptionNotFoundError,
    APIKeyNotFoundError
)

__version__ = "0.1.0"
__all__ = [
    # Main client
    "Client",

    # JWT token generation
    "AccessToken",

    # Webhook validation
    "RequestValidator",

    # Exceptions
    "VocaFuseError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "RecordingNotFoundError",
    "WebhookNotFoundError",
    "TranscriptionNotFoundError",
    "APIKeyNotFoundError"
] 