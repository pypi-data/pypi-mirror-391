"""
Voicenotes resource for VocaFuse SDK.
"""

from typing import Dict, Any, List, Optional
from .base import BaseResource


class TranscriptionResource:
    """Nested transcription resource for a specific voicenote."""
    
    def __init__(self, voicenotes_resource, voicenote_id: str):
        self.voicenotes_resource = voicenotes_resource
        self.voicenote_id = voicenote_id
    
    def get(self) -> Dict[str, Any]:
        """
        Get transcription for this voicenote.
        
        Returns:
            Transcription data including text, confidence, words, etc.
            
        Raises:
            TranscriptionNotFoundError: If transcription not found or not ready
            RecordingNotFoundError: If voicenote doesn't exist
        """
        return self.voicenotes_resource._get(f'voicenotes/{self.voicenote_id}/transcription')


class VoicenoteInstance:
    """Individual voicenote instance with nested resource access."""
    
    def __init__(self, voicenotes_resource, voicenote_id: str):
        self.voicenotes_resource = voicenotes_resource
        self.voicenote_id = voicenote_id
        self.transcription = TranscriptionResource(voicenotes_resource, voicenote_id)
    
    def get(self) -> Dict[str, Any]:
        """Get this specific voicenote."""
        return self.voicenotes_resource.get(self.voicenote_id)
    
    def delete(self) -> Dict[str, Any]:
        """Delete this specific voicenote."""
        return self.voicenotes_resource.delete(self.voicenote_id)


class VoicenotesResource(BaseResource):
    """
    Voicenotes resource for managing voice voicenotes.
    
    Usage:
        # List all voicenotes
        voicenotes = client.voicenotes.list()
        
        # Get specific voicenote
        voicenote = client.voicenotes.get('voicenote_id')
        
        # Get transcription (nested access)
        transcription = client.voicenotes('voicenote_id').transcription.get()
        
        # Delete voicenote
        client.voicenotes.delete('voicenote_id')
        
        # Or using instance access
        voicenote_instance = client.voicenotes('voicenote_id')
        voicenote_data = voicenote_instance.get()
        transcription = voicenote_instance.transcription.get()
        voicenote_instance.delete()
    """
    
    def __call__(self, voicenote_id: str) -> VoicenoteInstance:
        """
        Get voicenote instance for nested access.
        
        Args:
            voicenote_id: ID of the voicenote
            
        Returns:
            VoicenoteInstance with transcription access
        """
        return VoicenoteInstance(self, voicenote_id)
    
    def list(
        self,
        page: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List voicenotes with optional filtering.
        
        Args:
            page: Page number (0-based)
            limit: Number of voicenotes per page (max 100)
            status: Filter by status (processing, completed, failed)
            date_from: Filter voicenotes from this date (ISO format)
            date_to: Filter voicenotes to this date (ISO format)
            
        Returns:
            Dict with voicenotes list and pagination info
        """
        params = {
            'page': page,
            'limit': min(limit, 100)  # Enforce max limit
        }
        
        # Add optional filters
        if status:
            params['status'] = status
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        return self._get('voicenotes', params=params)
    
    def get(self, voicenote_id: str) -> Dict[str, Any]:
        """
        Get specific voicenote by ID.
        
        Args:
            voicenote_id: ID of the voicenote
            
        Returns:
            Recording data including metadata, status, etc.
            
        Raises:
            RecordingNotFoundError: If voicenote not found
        """
        return self._get(f'voicenotes/{voicenote_id}')
    
    def delete(self, voicenote_id: str) -> Dict[str, Any]:
        """
        Delete specific voicenote by ID.
        
        Args:
            voicenote_id: ID of the voicenote to delete
            
        Returns:
            Empty dict (204 No Content)
            
        Raises:
            RecordingNotFoundError: If voicenote not found
        """
        return self._delete(f'voicenotes/{voicenote_id}') 