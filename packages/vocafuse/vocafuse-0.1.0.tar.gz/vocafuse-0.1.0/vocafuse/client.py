"""
VocaFuse SDK Client - Main client class for API interactions.
"""

import requests
from typing import Optional
from .resources import VoicenotesResource, WebhooksResource, APIKeysResource, AccountResource


class Client:
    """
    Main VocaFuse API client.

    REQUIRED: This class is essential for the SDK to function as it:
    - Handles authentication and session management
    - Provides the main API interface (client.voicenotes, client.webhooks, etc.)
    - Orchestrates all resource classes

    Usage:
        import os
        from vocafuse import Client

        # Auto-detects environment from API key prefix
        client = Client(
            api_key=os.environ["VOCAFUSE_API_KEY"],
            api_secret=os.environ["VOCAFUSE_API_SECRET"]
        )

        # List voicenotes
        voicenotes = client.voicenotes.list()

        # Get specific voicenote
        voicenote = client.voicenotes.get('voicenote_id')

        # Get transcription (nested access)
        transcription = client.voicenotes('voicenote_id').transcription.get()

        # Manage webhooks
        webhook = client.webhooks.create(
            url='https://myapp.com/webhooks',
            events=['voicenote.completed']
        )
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: Optional[str] = None
    ):
        """
        Initialize the VocaFuse API client.
        
        Args:
            api_key: Your VocaFuse API key
            api_secret: Your VocaFuse API secret  
            base_url: API base URL (auto-detected if not provided)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Auto-detect environment from API key prefix
        if base_url is None:
            base_url = self._detect_base_url(api_key)
        
        self.base_url = base_url.rstrip('/')
        
        # Set up HTTP session with authentication headers
        self.session = requests.Session()
        self.session.headers.update({
            'X-VocaFuse-API-Key': self.api_key,
            'X-VocaFuse-API-Secret': self.api_secret,
            'Content-Type': 'application/json',
            'User-Agent': 'VocaFuse-Python-SDK/0.1.0'
        })
        
        # Initialize resources
        self.voicenotes = VoicenotesResource(self)
        self.webhooks = WebhooksResource(self)
        self.api_keys = APIKeysResource(self)
        self.account = AccountResource(self)
    
    def _detect_base_url(self, api_key: str) -> str:
        """Auto-detect API base URL from API key prefix."""
        return 'https://api.vocafuse.com'
    
    def __repr__(self):
        """String representation of the client."""
        env = 'live' if self.api_key.startswith('sk_live_') else 'test' if self.api_key.startswith('sk_test_') else 'dev'
        return f"Client(environment='{env}', base_url='{self.base_url}')" 