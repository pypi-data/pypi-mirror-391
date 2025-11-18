"""
Zetsubou.life Python SDK

A comprehensive Python SDK for the Zetsubou.life API v2.
Provides easy access to AI tools, encrypted file storage, chat, and webhooks.

Example:
    >>> from zetsubou import ZetsubouClient
    >>> client = ZetsubouClient(api_key="ztb_live_your_key_here")
    >>> tools = client.tools.list()
    >>> job = client.tools.execute("remove_bg", files=["image.jpg"])
"""

from .client import ZetsubouClient
from .exceptions import (
    ZetsubouError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError,
    WebhookError
)
from .models import (
    Tool,
    Job,
    VFSNode,
    ChatConversation,
    ChatMessage,
    Webhook,
    Account,
    StorageQuota
)

__version__ = "1.0.2"
__author__ = "Zetsubou.life"
__email__ = "support@zetsubou.life"

__all__ = [
    "ZetsubouClient",
    "ZetsubouError",
    "AuthenticationError", 
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "ServerError",
    "WebhookError",
    "Tool",
    "Job",
    "VFSNode",
    "ChatConversation", 
    "ChatMessage",
    "Webhook",
    "Account",
    "StorageQuota"
]