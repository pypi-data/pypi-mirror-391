"""
VocaFuse SDK Exceptions - Custom error handling for API responses.
"""


class VocaFuseError(Exception):
    """Base exception for all VocaFuse SDK errors."""
    
    def __init__(self, message, status_code=None, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(VocaFuseError):
    """Raised when API key authentication fails (401)."""
    pass


class AuthorizationError(VocaFuseError):
    """Raised when API key lacks required permissions (403)."""
    pass


class ValidationError(VocaFuseError):
    """Raised when request validation fails (400)."""
    pass


class NotFoundError(VocaFuseError):
    """Raised when requested resource is not found (404)."""
    pass


class ConflictError(VocaFuseError):
    """Raised when request conflicts with current state (409)."""
    pass


class RateLimitError(VocaFuseError):
    """Raised when rate limit is exceeded (429)."""
    pass


class ServerError(VocaFuseError):
    """Raised when server encounters an error (5xx)."""
    pass


class RecordingNotFoundError(NotFoundError):
    """Raised when a specific recording is not found."""
    pass


class WebhookNotFoundError(NotFoundError):
    """Raised when a specific webhook is not found."""
    pass


class TranscriptionNotFoundError(NotFoundError):
    """Raised when transcription is not found or not ready."""
    pass


class APIKeyNotFoundError(NotFoundError):
    """Raised when API key is not found."""
    pass


def handle_api_error(response):
    """Convert HTTP response to appropriate VocaFuse exception."""
    status_code = response.status_code
    
    try:
        error_data = response.json()
        error_info = error_data.get('error', {})
        message = error_info.get('message', f'HTTP {status_code} error')
        error_code = error_info.get('code')
        details = error_info.get('details', {})
    except (ValueError, KeyError):
        message = f'HTTP {status_code} error'
        error_code = None
        details = {}
    
    # Map status codes to specific exceptions
    if status_code == 401:
        raise AuthenticationError(message, status_code, error_code, details)
    elif status_code == 403:
        raise AuthorizationError(message, status_code, error_code, details)
    elif status_code == 400:
        raise ValidationError(message, status_code, error_code, details)
    elif status_code == 404:
        # Check for specific resource types
        if 'recording' in message.lower():
            raise RecordingNotFoundError(message, status_code, error_code, details)
        elif 'webhook' in message.lower():
            raise WebhookNotFoundError(message, status_code, error_code, details)
        elif 'transcription' in message.lower():
            raise TranscriptionNotFoundError(message, status_code, error_code, details)
        elif 'api key' in message.lower():
            raise APIKeyNotFoundError(message, status_code, error_code, details)
        else:
            raise NotFoundError(message, status_code, error_code, details)
    elif status_code == 409:
        raise ConflictError(message, status_code, error_code, details)
    elif status_code == 429:
        raise RateLimitError(message, status_code, error_code, details)
    elif status_code >= 500:
        raise ServerError(message, status_code, error_code, details)
    else:
        raise VocaFuseError(message, status_code, error_code, details) 