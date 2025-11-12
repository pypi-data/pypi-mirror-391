"""
VocaFuse Access Token - JWT token generation.
"""

import requests
from typing import Optional, List, Dict, Any
from ..exceptions import handle_api_error


class AccessToken:
    """
    VocaFuse Access Token generator.
    
    Usage:
        from vocafuse.jwt.access_token import AccessToken
        
        token = AccessToken(
            api_key='your-api-key',
            api_secret='your-api-secret',
            identity='user_123'
        )
        
        # Generate token (callable interface)
        response = token()
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        identity: str,
        base_url: Optional[str] = None
    ):
        """
        Initialize AccessToken generator.
        
        Args:
            api_key: Your VocaFuse API key
            api_secret: Your VocaFuse API secret
            identity: User identifier from your system
            base_url: API base URL (auto-detected if not provided)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.identity = identity
        
        # Auto-detect environment from API key prefix
        if base_url is None:
            base_url = self._detect_base_url(api_key)
        
        self.base_url = base_url.rstrip('/')
        
        # Set up HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'X-VocaFuse-API-Key': self.api_key,
            'X-VocaFuse-API-Secret': self.api_secret,
            'Content-Type': 'application/json',
            'User-Agent': 'VocaFuse-Python-SDK/0.1.0'
        })
    
    def _detect_base_url(self, api_key: str) -> str:
        """Auto-detect API base URL from API key prefix."""
        return 'https://api.vocafuse.com'
    

    def __call__(
        self,
        expires_in: Optional[int] = None,
        scopes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate token and return full response.
        
        Uses the identity provided during initialization.
        """
        data = {
            'user_id': self.identity
        }
        
        if expires_in is not None:
            data['expires_in'] = expires_in
            
        if scopes is not None:
            data['scopes'] = scopes
        else:
            data['scopes'] = ['voice-api.upload_recording']
        
        try:
            response = self.session.post(
                f"{self.base_url}/token",
                json=data
            )
            
            if not response.ok:
                handle_api_error(response)
            
            return response.json()
            
        except requests.RequestException as e:
            raise Exception(f"Token generation failed: {str(e)}")
    
    def __repr__(self):
        """String representation."""
        env = 'live' if self.api_key.startswith('sk_live_') else 'test' if self.api_key.startswith('sk_test_') else 'dev'
        return f"AccessToken(environment='{env}')" 