"""
Zetsubou.life SDK Data Models

Data classes representing API responses and entities.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


@dataclass
class Tool:
    """Represents a tool available in the API."""
    id: str
    name: str
    description: Optional[str]
    category: str
    input_type: str
    output_type: str
    required_tier: str
    accessible: bool
    options: Dict[str, Any]
    supports_audio: bool = False
    supports_batch: bool = False
    timeout_seconds: int = 600

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tool':
        """Create Tool from API response."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            category=data['category'],
            input_type=data['input_type'],
            output_type=data['output_type'],
            required_tier=data['required_tier'],
            accessible=data['accessible'],
            options=data.get('options', {}),
            supports_audio=data.get('supports_audio', False),
            supports_batch=data.get('supports_batch', False),
            timeout_seconds=data.get('timeout_seconds', 600)
        )


@dataclass
class Job:
    """Represents an asynchronous job."""
    id: str
    tool_id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: int
    error: Optional[str]
    inputs: List[str]
    outputs: List[str]
    options: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create Job from API response."""
        return cls(
            id=data.get('id') or data.get('job_id'),  # Support both id and job_id
            tool_id=data.get('tool_id') or data.get('tool'),  # Support both formats
            status=data['status'],
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at'].replace('Z', '+00:00')) if data.get('completed_at') else None,
            progress=data.get('progress', 0),
            error=data.get('error'),
            inputs=data.get('inputs') or data.get('input_files', []),  # Support both formats
            outputs=data.get('outputs') or data.get('output_files', []),  # Support both formats
            options=data.get('options', {})
        )


@dataclass
class VFSNode:
    """Represents a VFS node (file or folder)."""
    id: str
    name: str
    type: str  # 'file' or 'folder'
    size_bytes: int
    mime_type: Optional[str]
    created_at: datetime
    updated_at: datetime
    parent_id: Optional[str]
    is_encrypted: bool
    download_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VFSNode':
        """Create VFSNode from API response."""
        return cls(
            id=data['id'],
            name=data['name'],
            type=data['type'],
            size_bytes=data['size_bytes'],
            mime_type=data.get('mime_type'),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')),
            parent_id=data.get('parent_id'),
            is_encrypted=data.get('is_encrypted', False),
            download_url=data.get('download_url')
        )


@dataclass
class ChatMessage:
    """Represents a chat message."""
    id: int
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create ChatMessage from API response."""
        return cls(
            id=data['id'],
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        )


@dataclass
class ChatConversation:
    """Represents a chat conversation."""
    id: int
    title: str
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[ChatMessage] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatConversation':
        """Create ChatConversation from API response."""
        last_message = None
        if data.get('last_message'):
            last_message = ChatMessage.from_dict(data['last_message'])
        
        return cls(
            id=data['id'],
            title=data['title'],
            model=data['model'],
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')),
            message_count=data['message_count'],
            last_message=last_message
        )


@dataclass
class Webhook:
    """Represents a webhook configuration."""
    id: int
    url: str
    events: List[str]
    enabled: bool
    success_count: int
    failure_count: int
    last_delivery_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Webhook':
        """Create Webhook from API response."""
        return cls(
            id=data['id'],
            url=data['url'],
            events=data['events'],
            enabled=data['enabled'],
            success_count=data.get('success_count', 0),
            failure_count=data.get('failure_count', 0),
            last_delivery_at=datetime.fromisoformat(data['last_delivery_at'].replace('Z', '+00:00')) if data.get('last_delivery_at') else None,
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        )


@dataclass
class Account:
    """Represents user account information."""
    user_id: int
    username: str
    email: str
    tier: str
    created_at: datetime
    subscription: Dict[str, Any]
    usage: Dict[str, Any]
    features: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """Create Account from API response."""
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            tier=data['tier'],
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            subscription=data.get('subscription', {}),
            usage=data.get('usage', {}),
            features=data.get('features', {})
        )


@dataclass
class StorageQuota:
    """Represents storage quota information."""
    tier: str
    quota_bytes: int
    used_bytes: int
    available_bytes: int
    usage_percent: float
    file_count: int
    folder_count: int
    breakdown: Dict[str, Any]
    largest_files: List[Dict[str, Any]]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorageQuota':
        """Create StorageQuota from API response."""
        return cls(
            tier=data['tier'],
            quota_bytes=int(data['quota_bytes']),
            used_bytes=int(data['used_bytes']),
            available_bytes=int(data['available_bytes']),
            usage_percent=float(data['usage_percent']),
            file_count=data['file_count'],
            folder_count=data['folder_count'],
            breakdown=data.get('breakdown', {}),
            largest_files=data.get('largest_files', [])
        )