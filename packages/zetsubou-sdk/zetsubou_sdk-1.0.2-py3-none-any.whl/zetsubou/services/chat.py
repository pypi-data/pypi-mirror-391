"""
Chat Service

Handles chat conversations and message management.
"""

from typing import List, Dict, Any, Optional, Union
from ..models import ChatConversation, ChatMessage
from ..exceptions import ZetsubouError


class ChatService:
    """Service for managing chat conversations and messages."""
    
    def __init__(self, client):
        self.client = client
    
    def list_conversations(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatConversation]:
        """
        List all chat conversations.
        
        Args:
            limit: Number of results per page
            offset: Pagination offset
            
        Returns:
            List of ChatConversation objects
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        response = self.client.get('/api/v2/chat/conversations', params=params)
        data = response.json()
        return [ChatConversation.from_dict(conv) for conv in data['conversations']]
    
    def create_conversation(
        self,
        title: str,
        model: str = "llama3.2",
        system_prompt: Optional[str] = None
    ) -> ChatConversation:
        """
        Create a new chat conversation.
        
        Args:
            title: Conversation title
            model: AI model to use
            system_prompt: Optional system prompt
            
        Returns:
            ChatConversation object
        """
        data = {
            'title': title,
            'model': model
        }
        if system_prompt:
            data['system_prompt'] = system_prompt
        
        response = self.client.post('/api/v2/chat/conversations', data=data)
        result = response.json()
        return ChatConversation.from_dict(result['conversation'])
    
    def get_conversation(self, conversation_id: int) -> ChatConversation:
        """
        Get details for a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            ChatConversation object
        """
        # Note: This endpoint might not exist in the current API
        # We'll implement it as a placeholder for future use
        conversations = self.list_conversations(limit=1000)
        for conv in conversations:
            if conv.id == conversation_id:
                return conv
        
        raise ZetsubouError(f"Conversation {conversation_id} not found")
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """
        Delete a chat conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deletion was successful
        """
        response = self.client.delete(f'/api/v2/chat/conversations/{conversation_id}')
        data = response.json()
        return data.get('success', False)
    
    def get_messages(self, conversation_id: int) -> List[ChatMessage]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of ChatMessage objects
        """
        response = self.client.get(f'/api/v2/chat/conversations/{conversation_id}/messages')
        data = response.json()
        return [ChatMessage.from_dict(msg) for msg in data['messages']]
    
    def send_message(
        self,
        conversation_id: int,
        content: str
    ) -> ChatMessage:
        """
        Send a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            
        Returns:
            ChatMessage object
        """
        data = {'content': content}
        
        response = self.client.post(
            f'/api/v2/chat/conversations/{conversation_id}/messages',
            data=data
        )
        result = response.json()
        return ChatMessage.from_dict(result['message'])
    
    def export_conversation(
        self,
        conversation_id: int,
        format: str = "json"
    ) -> Union[Dict[str, Any], str]:
        """
        Export a conversation in JSON or Markdown format.
        
        Args:
            conversation_id: Conversation ID
            format: Export format ('json' or 'md')
            
        Returns:
            Exported conversation data
        """
        params = {'format': format}
        response = self.client.get(
            f'/api/v2/chat/conversations/{conversation_id}/export',
            params=params
        )
        
        if format == 'json':
            return response.json()
        else:
            return response.text
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available AI models.
        
        Returns:
            List of model names
        """
        # Note: This would require a separate API endpoint
        # For now, return common models
        return [
            "llama3.2",
            "qwen2.5-vl",
            "glm-4.6:cloud",
            "auto"
        ]
    
    def create_and_send_message(
        self,
        title: str,
        content: str,
        model: str = "llama3.2",
        system_prompt: Optional[str] = None
    ) -> tuple[ChatConversation, ChatMessage]:
        """
        Create a new conversation and send the first message.
        
        Args:
            title: Conversation title
            content: First message content
            model: AI model to use
            system_prompt: Optional system prompt
            
        Returns:
            Tuple of (ChatConversation, ChatMessage) objects
        """
        conversation = self.create_conversation(title, model, system_prompt)
        message = self.send_message(conversation.id, content)
        return conversation, message