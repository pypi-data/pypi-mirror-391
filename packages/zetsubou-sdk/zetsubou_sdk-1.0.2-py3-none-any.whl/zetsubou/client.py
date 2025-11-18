"""
Zetsubou.life API Client

Main client class that provides access to all API v2 functionality.
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List, Union, BinaryIO
from urllib.parse import urljoin

from .exceptions import (
    ZetsubouError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError
)
from .models import Tool, Job, VFSNode, ChatConversation, ChatMessage, Webhook, Account, StorageQuota
from .services import ToolsService, JobsService, VFSService, ChatService, WebhooksService, AccountService


class ZetsubouClient:
    """
    Main client for interacting with the Zetsubou.life API v2.
    
    Args:
        api_key: Your API key (starts with 'ztb_live_')
        base_url: API base URL (default: https://zetsubou.life)
        timeout: Request timeout in seconds (default: 30)
        retry_attempts: Number of retry attempts for failed requests (default: 3)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://zetsubou.life",
        timeout: int = 30,
        retry_attempts: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        
        # Initialize session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'User-Agent': f'zetsubou-sdk-python/{__import__("zetsubou").__version__}',
            'Content-Type': 'application/json'
        })
        
        # Initialize service modules
        self.tools = ToolsService(self)
        self.jobs = JobsService(self)
        self.vfs = VFSService(self)
        self.chat = ChatService(self)
        self.webhooks = WebhooksService(self)
        self.account = AccountService(self)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> requests.Response:
        """
        Make an HTTP request to the API with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (e.g., '/api/v2/tools')
            params: Query parameters
            data: Request body data
            files: Files to upload (for multipart requests)
            stream: Whether to stream the response
            
        Returns:
            requests.Response object
            
        Raises:
            ZetsubouError: For various API errors
        """
        url = urljoin(self.base_url, endpoint)
        
        # Prepare headers
        headers = {}
        if files:
            # Remove Content-Type for multipart requests
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
        
        # Retry logic
        last_exception = None
        for attempt in range(self.retry_attempts + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data if not files else None,
                    data=data if files else None,
                    files=files,
                    headers=headers,
                    timeout=self.timeout,
                    stream=stream
                )
                
                # Handle different status codes
                if response.status_code == 200:
                    return response
                elif response.status_code == 201:
                    return response
                elif response.status_code == 204:
                    return response
                elif response.status_code == 400:
                    error_data = self._parse_error_response(response)
                    raise ValidationError(error_data.get('message', 'Validation error'), error_data)
                elif response.status_code == 401:
                    error_data = self._parse_error_response(response)
                    raise AuthenticationError(error_data.get('message', 'Authentication failed'), error_data)
                elif response.status_code == 404:
                    error_data = self._parse_error_response(response)
                    raise NotFoundError(error_data.get('message', 'Resource not found'), error_data)
                elif response.status_code == 429:
                    error_data = self._parse_error_response(response)
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitError(
                        error_data.get('message', 'Rate limit exceeded'),
                        error_data,
                        retry_after=retry_after
                    )
                elif 500 <= response.status_code < 600:
                    error_data = self._parse_error_response(response)
                    if attempt < self.retry_attempts:
                        # Retry on server errors
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise ServerError(error_data.get('message', 'Server error'), error_data)
                else:
                    error_data = self._parse_error_response(response)
                    raise ZetsubouError(
                        f"Unexpected status code {response.status_code}: {error_data.get('message', 'Unknown error')}",
                        error_data
                    )
                    
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                if attempt < self.retry_attempts:
                    time.sleep(2 ** attempt)
                    continue
                raise ZetsubouError(f"Request failed after {self.retry_attempts} retries: {str(e)}")
            except ZetsubouError:
                # Re-raise our custom errors immediately
                raise
            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts:
                    time.sleep(2 ** attempt)
                    continue
                raise ZetsubouError(f"Unexpected error: {str(e)}")
        
        # If we get here, all retries failed
        raise ZetsubouError(f"Request failed after {self.retry_attempts} retries: {str(last_exception)}")
    
    def _parse_error_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse error response from API."""
        try:
            return response.json()
        except (ValueError, KeyError):
            return {
                'message': response.text or f'HTTP {response.status_code}',
                'code': f'HTTP_{response.status_code}',
                'status_code': response.status_code
            }
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a GET request."""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a POST request."""
        return self._make_request('POST', endpoint, data=data, files=files)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a PUT request."""
        return self._make_request('PUT', endpoint, data=data)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a PATCH request."""
        return self._make_request('PATCH', endpoint, data=data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """Make a DELETE request."""
        return self._make_request('DELETE', endpoint)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Health status information
        """
        response = self.get('/health')
        return response.json()
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()