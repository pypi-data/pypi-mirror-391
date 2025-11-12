"""
Account resource for VocaFuse SDK.
"""

from typing import Dict, Any
from .base import BaseResource


class AccountResource(BaseResource):
    """
    Account resource for managing account information.
    
    Usage:
        # Get account info
        account = client.account.get()
        
        # Update account settings
        updated = client.account.update(
            name='New Company Name',
            webhook_url='https://myapp.com/webhooks'
        )
    """
    
    def get(self) -> Dict[str, Any]:
        """
        Get account information and settings.
        
        Returns:
            Account data including tenant info, settings, usage stats, etc.
        """
        return self._get('account')
    
    def update(self, **kwargs) -> Dict[str, Any]:
        """
        Update account settings.
        
        Args:
            **kwargs: Account fields to update (name, webhook_url, etc.)
            
        Returns:
            Updated account information
            
        Raises:
            ValidationError: If provided data is invalid
        """
        return self._put('account', data=kwargs) 