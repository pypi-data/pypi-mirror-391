"""
Webhooks Service

Handles webhook management and event subscriptions.
"""

from typing import List, Dict, Any, Optional
from ..models import Webhook
from ..exceptions import ZetsubouError


class WebhooksService:
    """Service for managing webhooks and event subscriptions."""
    
    def __init__(self, client):
        self.client = client
    
    def list(self) -> List[Webhook]:
        """
        List all webhooks for the current user.
        
        Returns:
            List of Webhook objects
        """
        response = self.client.get('/api/v2/webhooks')
        data = response.json()
        return [Webhook.from_dict(webhook) for webhook in data['webhooks']]
    
    def create(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Create a new webhook.
        
        Args:
            url: Webhook URL
            events: List of event types to subscribe to
            secret: Optional webhook secret for signature verification
            
        Returns:
            Webhook object
        """
        data = {
            'url': url,
            'events': events
        }
        if secret:
            data['secret'] = secret
        
        response = self.client.post('/api/v2/webhooks', data=data)
        result = response.json()
        return Webhook.from_dict(result['webhook'])
    
    def get(self, webhook_id: int) -> Webhook:
        """
        Get details for a specific webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            Webhook object
        """
        response = self.client.get(f'/api/v2/webhooks/{webhook_id}')
        data = response.json()
        return Webhook.from_dict(data['webhook'])
    
    def update(
        self,
        webhook_id: int,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        secret: Optional[str] = None,
        enabled: Optional[bool] = None
    ) -> Webhook:
        """
        Update a webhook configuration.
        
        Args:
            webhook_id: Webhook ID
            url: New webhook URL
            events: New list of event types
            secret: New webhook secret
            enabled: Whether to enable/disable the webhook
            
        Returns:
            Updated Webhook object
        """
        data = {}
        if url is not None:
            data['url'] = url
        if events is not None:
            data['events'] = events
        if secret is not None:
            data['secret'] = secret
        if enabled is not None:
            data['enabled'] = enabled
        
        response = self.client.put(f'/api/v2/webhooks/{webhook_id}', data=data)
        result = response.json()
        return Webhook.from_dict(result['webhook'])
    
    def delete(self, webhook_id: int) -> bool:
        """
        Delete a webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            True if deletion was successful
        """
        response = self.client.delete(f'/api/v2/webhooks/{webhook_id}')
        data = response.json()
        return data.get('success', False)
    
    def test(self, webhook_id: int) -> bool:
        """
        Send a test event to a webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            True if test was sent successfully
        """
        response = self.client.post(f'/api/v2/webhooks/{webhook_id}/test')
        data = response.json()
        return data.get('success', False)
    
    def get_stats(self, webhook_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Get delivery statistics for a webhook.
        
        Args:
            webhook_id: Webhook ID
            days: Number of days to look back
            
        Returns:
            Statistics dictionary
        """
        params = {'days': days}
        response = self.client.get(f'/api/v2/webhooks/{webhook_id}/stats', params=params)
        return response.json()
    
    def get_available_events(self) -> Dict[str, str]:
        """
        Get available webhook event types.
        
        Returns:
            Dictionary mapping event types to descriptions
        """
        response = self.client.get('/api/v2/webhooks/events')
        data = response.json()
        return data['events']
    
    def create_job_webhook(
        self,
        url: str,
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Create a webhook for job events (completed, failed, cancelled).
        
        Args:
            url: Webhook URL
            secret: Optional webhook secret
            
        Returns:
            Webhook object
        """
        events = ['job.completed', 'job.failed', 'job.cancelled']
        return self.create(url, events, secret)
    
    def create_file_webhook(
        self,
        url: str,
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Create a webhook for file events (uploaded, downloaded).
        
        Args:
            url: Webhook URL
            secret: Optional webhook secret
            
        Returns:
            Webhook object
        """
        events = ['file.uploaded', 'file.downloaded']
        return self.create(url, events, secret)
    
    def create_storage_webhook(
        self,
        url: str,
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Create a webhook for storage events (quota warning, exceeded).
        
        Args:
            url: Webhook URL
            secret: Optional webhook secret
            
        Returns:
            Webhook object
        """
        events = ['storage.quota_warning', 'storage.quota_exceeded']
        return self.create(url, events, secret)
    
    def create_all_events_webhook(
        self,
        url: str,
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Create a webhook that subscribes to all available events.
        
        Args:
            url: Webhook URL
            secret: Optional webhook secret
            
        Returns:
            Webhook object
        """
        events = list(self.get_available_events().keys())
        return self.create(url, events, secret)