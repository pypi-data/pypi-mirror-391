"""
API Keys resource for VocaFuse SDK.
"""

from typing import Dict, Any, Optional
from .base import BaseResource


class APIKeysResource(BaseResource):
    """
    API Keys resource for managing API key lifecycle.
    
    Usage:
        # List API keys
        keys = client.api_keys.list()
        
        # Create new API key
        new_key = client.api_keys.create(name='Production Key')
        
        # Delete API key
        client.api_keys.delete('key_id')
    """
    
    def list(self) -> Dict[str, Any]:
        """
        List all API keys for the account.
        
        Returns:
            Dict with API keys list and metadata
        """
        return self._get('account/api-keys')
    
    def create(self, name: str) -> Dict[str, Any]:
        """
        Create a new API key.
        
        Args:
            name: Human-readable name for the API key
            
        Returns:
            Created API key with key and secret (only shown once)
            
        Raises:
            ValidationError: If name is invalid
        """
        data = {
            'name': name
        }
        
        return self._post('account/api-keys', data=data)
    
    def delete(self, api_key_id: str) -> Dict[str, Any]:
        """
        Delete an API key.
        
        Args:
            api_key_id: ID of the API key to delete
            
        Returns:
            Empty dict (204 No Content)
            
        Raises:
            APIKeyNotFoundError: If API key not found
        """
        return self._delete(f'account/api-keys/{api_key_id}') 