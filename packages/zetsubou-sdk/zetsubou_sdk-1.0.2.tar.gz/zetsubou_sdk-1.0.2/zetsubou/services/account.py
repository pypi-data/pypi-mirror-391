"""
Account Service

Handles account information, usage statistics, and API key management.
"""

from typing import List, Dict, Any, Optional
from ..models import Account, StorageQuota
from ..exceptions import ZetsubouError


class AccountService:
    """Service for managing account information and usage."""
    
    def __init__(self, client):
        self.client = client
    
    def get_account(self) -> Account:
        """
        Get current account information.
        
        Returns:
            Account object
        """
        response = self.client.get('/api/v2/account')
        data = response.json()
        return Account.from_dict(data)
    
    def get_storage_quota(self) -> StorageQuota:
        """
        Get detailed storage quota information.
        
        Returns:
            StorageQuota object
        """
        response = self.client.get('/api/v2/storage/quota')
        data = response.json()
        return StorageQuota.from_dict(data)
    
    def get_usage_stats(
        self,
        period: str = "30d",
        tool_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics for the account.
        
        Args:
            period: Time period ('7d', '30d', '90d', '1y')
            tool_id: Optional tool ID to filter by
            
        Returns:
            Usage statistics dictionary
        """
        params = {'period': period}
        if tool_id:
            params['tool_id'] = tool_id
        
        response = self.client.get('/api/v2/account/usage', params=params)
        return response.json()
    
    def list_api_keys(self) -> List[Dict[str, Any]]:
        """
        List all API keys for the account.
        
        Returns:
            List of API key information
        """
        response = self.client.get('/api/v2/account/api-keys')
        data = response.json()
        return data['api_keys']
    
    def create_api_key(
        self,
        name: str,
        scopes: List[str],
        expires_at: Optional[str] = None,
        drive_bypass: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new API key.
        
        Args:
            name: API key name
            scopes: List of permission scopes
            expires_at: Optional expiration date (ISO format)
            drive_bypass: Whether to bypass drive encryption requirement
            
        Returns:
            API key creation response
        """
        data = {
            'name': name,
            'scopes': scopes,
            'drive_bypass': drive_bypass
        }
        if expires_at:
            data['expires_at'] = expires_at
        
        response = self.client.post('/api/v2/account/api-keys', data=data)
        return response.json()
    
    def delete_api_key(self, key_id: int) -> bool:
        """
        Delete an API key.
        
        Args:
            key_id: API key ID
            
        Returns:
            True if deletion was successful
        """
        response = self.client.delete(f'/api/v2/account/api-keys/{key_id}')
        data = response.json()
        return data.get('success', False)
    
    def get_tier_info(self) -> Dict[str, Any]:
        """
        Get information about the current subscription tier.
        
        Returns:
            Tier information dictionary
        """
        account = self.get_account()
        return {
            'tier': account.tier,
            'subscription': account.subscription,
            'features': account.features
        }
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of tools available to the current tier.
        
        Returns:
            List of tool IDs
        """
        account = self.get_account()
        return account.features.get('tools', [])
    
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Get rate limit information for the current tier.
        
        Returns:
            Rate limit information
        """
        account = self.get_account()
        return {
            'max_concurrent_jobs': account.features.get('max_concurrent_jobs', 1),
            'rate_limit_per_minute': account.features.get('rate_limit_per_minute', 10)
        }
    
    def get_storage_usage_percentage(self) -> float:
        """
        Get current storage usage as a percentage.
        
        Returns:
            Usage percentage (0.0 to 100.0)
        """
        quota = self.get_storage_quota()
        return quota.usage_percent
    
    def is_storage_quota_warning(self, threshold: float = 80.0) -> bool:
        """
        Check if storage usage is above the warning threshold.
        
        Args:
            threshold: Warning threshold percentage (default: 80%)
            
        Returns:
            True if usage is above threshold
        """
        return self.get_storage_usage_percentage() >= threshold
    
    def get_largest_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the largest files in storage.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        quota = self.get_storage_quota()
        return quota.largest_files[:limit]
    
    def get_storage_breakdown(self) -> Dict[str, Any]:
        """
        Get storage breakdown by file type.
        
        Returns:
            Storage breakdown dictionary
        """
        quota = self.get_storage_quota()
        return quota.breakdown