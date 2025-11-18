"""
Tools Service

Handles tool execution, listing, and management.
"""

from typing import List, Dict, Any, Optional, Union, BinaryIO
from ..models import Tool, Job
from ..exceptions import ZetsubouError


class ToolsService:
    """Service for managing tools and tool execution."""
    
    def __init__(self, client):
        self.client = client
    
    def list(self) -> List[Tool]:
        """
        List all available tools.
        
        Returns:
            List of Tool objects
        """
        response = self.client.get('/api/v2/tools')
        data = response.json()
        return [Tool.from_dict(tool) for tool in data['tools']]
    
    def get(self, tool_id: str) -> Tool:
        """
        Get details for a specific tool.

        Args:
            tool_id: Tool identifier

        Returns:
            Tool object
        """
        response = self.client.get(f'/api/v2/tools/{tool_id}')
        data = response.json()
        return Tool.from_dict(data)
    
    def execute(
        self,
        tool_id: str,
        files: List[Union[str, BinaryIO]],
        options: Optional[Dict[str, Any]] = None,
        audio_files: Optional[List[Union[str, BinaryIO]]] = None
    ) -> Job:
        """
        Execute a tool with files and options.
        
        Args:
            tool_id: Tool identifier
            files: List of file paths or file-like objects
            options: Tool-specific options
            audio_files: Optional audio files for video tools
            
        Returns:
            Job object
        """
        # Prepare files for upload
        file_data = {}
        for i, file in enumerate(files):
            if isinstance(file, str):
                # File path
                with open(file, 'rb') as f:
                    file_data[f'file_{i}'] = (f.name, f.read())
            else:
                # File-like object
                file_data[f'file_{i}'] = file
        
        # Add audio files if provided
        if audio_files:
            for i, audio_file in enumerate(audio_files):
                if isinstance(audio_file, str):
                    with open(audio_file, 'rb') as f:
                        file_data[f'audio_{i}'] = (f.name, f.read())
                else:
                    file_data[f'audio_{i}'] = audio_file
        
        # Add options as form data
        form_data = {}
        if options:
            form_data['options'] = str(options)  # Convert to string for form data
        
        response = self.client.post(
            f'/api/v2/tools/{tool_id}/execute',
            files=file_data,
            data=form_data
        )
        data = response.json()
        return Job.from_dict(data['job'])
    
    def batch_execute(
        self,
        tool_id: str,
        files: List[Union[str, BinaryIO]],
        options: Optional[Dict[str, Any]] = None,
        audio_files: Optional[List[Union[str, BinaryIO]]] = None
    ) -> Job:
        """
        Execute a tool in batch mode on multiple files.
        
        Args:
            tool_id: Tool identifier
            files: List of file paths or file-like objects
            options: Tool-specific options
            audio_files: Optional audio files for video tools
            
        Returns:
            Job object
        """
        # Prepare files for upload
        file_data = {}
        for i, file in enumerate(files):
            if isinstance(file, str):
                with open(file, 'rb') as f:
                    file_data[f'file_{i}'] = (f.name, f.read())
            else:
                file_data[f'file_{i}'] = file
        
        # Add audio files if provided
        if audio_files:
            for i, audio_file in enumerate(audio_files):
                if isinstance(audio_file, str):
                    with open(audio_file, 'rb') as f:
                        file_data[f'audio_{i}'] = (f.name, f.read())
                else:
                    file_data[f'audio_{i}'] = audio_file
        
        # Add options as form data
        form_data = {}
        if options:
            form_data['options'] = str(options)
        
        response = self.client.post(
            f'/api/v2/tools/{tool_id}/batch',
            files=file_data,
            data=form_data
        )
        data = response.json()
        return Job.from_dict(data['job'])
    
    def create_chain(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a tool chain for automated processing.
        
        Args:
            name: Chain name
            steps: List of chain steps with tool_id and options
            description: Optional chain description
            
        Returns:
            Chain creation response
        """
        data = {
            'name': name,
            'steps': steps
        }
        if description:
            data['description'] = description
        
        response = self.client.post('/api/v2/chains', data=data)
        return response.json()
    
    def list_chains(self) -> List[Dict[str, Any]]:
        """
        List all tool chains.
        
        Returns:
            List of chain information
        """
        response = self.client.get('/api/v2/chains')
        data = response.json()
        return data['chains']
    
    def get_chain(self, chain_id: int) -> Dict[str, Any]:
        """
        Get details for a specific chain.
        
        Args:
            chain_id: Chain identifier
            
        Returns:
            Chain details
        """
        response = self.client.get(f'/api/v2/chains/{chain_id}')
        return response.json()