"""
VocaFuse Request Validator - Webhook signature verification.
"""

import hmac
import hashlib
from typing import Optional


class RequestValidator:
    """
    VocaFuse Request Validator.
    
    Usage:
        from vocafuse.webhook.request_validator import RequestValidator
        
        validator = RequestValidator('your-webhook-secret')
        
        # Validate webhook request
        is_valid = validator.validate(
            payload='{"event":"recording.completed"}',
            signature='sha256=abc123...',
            url='https://myapp.com/webhook'  # optional
        )
    """
    
    def __init__(self, auth_token: str):
        """
        Initialize RequestValidator.
        
        Args:
            auth_token: Your webhook secret/auth token
        """
        self.auth_token = auth_token
    
    def validate(
        self,
        payload: str,
        signature: str,
        url: Optional[str] = None,
        timestamp: Optional[str] = None,
        delivery_id: Optional[str] = None
    ) -> bool:
        """
        Validate webhook signature.
        
        Args:
            payload: Raw webhook payload
            signature: Webhook signature from headers
            url: Webhook URL (optional, for additional validation)
            timestamp: Webhook timestamp (optional)
            delivery_id: Webhook delivery ID (optional, for enhanced security)
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Create expected signature using VocaFuse format: {timestamp}.{delivery_id}.{payload}
        if timestamp and delivery_id:
            string_to_sign = f"{timestamp}.{delivery_id}.{payload}"
        elif timestamp:
            string_to_sign = f"{timestamp}.{payload}"
        else:
            string_to_sign = payload
            
        expected_signature = hmac.new(
            self.auth_token.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Handle different signature formats
        if signature.startswith('sha256='):
            signature = signature[7:]  # Remove 'sha256=' prefix
        
        # Compare signatures (constant time comparison)
        return hmac.compare_digest(
            signature.lower(),
            expected_signature.lower()
        )
    
    def compute_signature(
        self,
        payload: str,
        timestamp: Optional[str] = None,
        delivery_id: Optional[str] = None
    ) -> str:
        """
        Compute signature for a payload (useful for testing).
        
        Args:
            payload: Raw payload to sign
            timestamp: Optional timestamp
            delivery_id: Optional delivery ID
            
        Returns:
            Computed signature
        """
        # Use VocaFuse format: {timestamp}.{delivery_id}.{payload}
        if timestamp and delivery_id:
            string_to_sign = f"{timestamp}.{delivery_id}.{payload}"
        elif timestamp:
            string_to_sign = f"{timestamp}.{payload}"
        else:
            string_to_sign = payload
            
        return hmac.new(
            self.auth_token.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def __repr__(self):
        """String representation."""
        return f"RequestValidator(auth_token='***')" 