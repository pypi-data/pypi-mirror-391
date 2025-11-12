"""
Webhooks resource for VocaFuse SDK.
"""

import hmac
import hashlib
from typing import Dict, Any, List, Optional
from .base import BaseResource


class WebhooksResource(BaseResource):
    """
    Webhooks resource for managing webhook configurations and verifying signatures.

    Usage:
        # List webhooks
        webhooks = client.webhooks.list()

        # Create webhook
        webhook = client.webhooks.create(
            url='https://myapp.com/webhooks',
            events=['recording.completed', 'recording.failed'],
            secret='my-webhook-secret'
        )

        # Update webhook
        updated = client.webhooks.update(
            webhook_id='webhook_id',
            url='https://myapp.com/new-webhook',
            events=['recording.completed']
        )

        # Delete webhook
        client.webhooks.delete('webhook_id')

        # Verify webhook signature
        is_valid = client.webhooks.verify(
            payload='{"event":"recording.completed"}',
            signature='sha256=abc123...',
            secret='my-webhook-secret'
        )
    """
    
    def list(self) -> Dict[str, Any]:
        """
        List all webhook configurations for the tenant.
        
        Returns:
            Dict with webhooks list and metadata
        """
        return self._get('webhooks')
    
    def create(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new webhook configuration.
        
        Args:
            url: Webhook URL endpoint
            events: List of events to subscribe to
            secret: Optional webhook secret for signature verification
            
        Returns:
            Created webhook configuration
            
        Raises:
            ValidationError: If URL or events are invalid
            ConflictError: If webhook already exists (single webhook per tenant)
        """
        data = {
            'url': url,
            'events': events
        }
        
        if secret is not None:
            data['secret'] = secret
        
        return self._post('webhooks', data=data)
    
    def update(
        self,
        webhook_id: str,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update existing webhook configuration.
        
        Args:
            webhook_id: ID of the webhook to update
            url: New webhook URL endpoint
            events: New list of events to subscribe to  
            secret: New webhook secret (optional)
            
        Returns:
            Updated webhook configuration
            
        Raises:
            WebhookNotFoundError: If webhook not found
            ValidationError: If URL or events are invalid
        """
        data = {
            'url': url,
            'events': events
        }
        
        if secret is not None:
            data['secret'] = secret
        
        return self._put(f'webhooks/{webhook_id}', data=data)
    
    def delete(self, webhook_id: str) -> Dict[str, Any]:
        """
        Delete webhook configuration.

        Args:
            webhook_id: ID of the webhook to delete

        Returns:
            Empty dict (204 No Content)

        Raises:
            WebhookNotFoundError: If webhook not found
        """
        return self._delete(f'webhooks/{webhook_id}')

    def verify(
        self,
        payload: str,
        signature: str,
        secret: str,
        url: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Verify webhook signature using HMAC-SHA256.

        Args:
            payload: Raw webhook payload (JSON string)
            signature: Webhook signature from X-VocaFuse-Signature header
            secret: Webhook secret configured for this webhook
            url: Webhook URL (optional, for additional validation)
            timestamp: Webhook timestamp (optional)

        Returns:
            True if signature is valid, False otherwise

        Example:
            ```python
            payload = request.get_data(as_text=True)
            signature = request.headers.get('X-VocaFuse-Signature')
            secret = 'your-webhook-secret'

            is_valid = client.webhooks.verify(payload, signature, secret)
            ```
        """
        # Create expected signature
        if timestamp:
            string_to_sign = f"{timestamp}.{payload}"
        else:
            string_to_sign = payload

        expected_signature = hmac.new(
            secret.encode('utf-8'),
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