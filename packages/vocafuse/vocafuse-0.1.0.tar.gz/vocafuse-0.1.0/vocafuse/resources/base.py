"""
Base resource class for VocaFuse SDK resources.
"""

import requests
from typing import Dict, Any, Optional
from ..exceptions import handle_api_error


class BaseResource:
    """Base class for all VocaFuse API resources."""
    
    def __init__(self, client):
        self.client = client
        self.base_url = client.base_url
        self.session = client.session
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle non-2xx responses
            if not response.ok:
                handle_api_error(response)
            
            # Handle 204 No Content responses
            if response.status_code == 204:
                return {}
            
            # Parse JSON response
            return response.json()
            
        except requests.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        return self._request('GET', endpoint, params=params)
    
    def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request."""
        return self._request('POST', endpoint, json=data)
    
    def _put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request."""
        return self._request('PUT', endpoint, json=data)
    
    def _delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._request('DELETE', endpoint) 