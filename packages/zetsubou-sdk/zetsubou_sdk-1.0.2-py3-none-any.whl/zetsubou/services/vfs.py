"""
VFS Service

Handles Virtual File System operations including file upload, download, and management.
"""

from typing import List, Dict, Any, Optional, Union, BinaryIO
from ..models import VFSNode
from ..exceptions import ZetsubouError


class VFSService:
    """Service for managing the Virtual File System."""
    
    def __init__(self, client):
        self.client = client
    
    def list_nodes(
        self,
        parent_id: Optional[str] = None,
        node_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[VFSNode]:
        """
        List VFS nodes (files and folders).
        
        Args:
            parent_id: Filter by parent folder ID
            node_type: Filter by node type ('file' or 'folder')
            limit: Number of results per page
            offset: Pagination offset
            
        Returns:
            List of VFSNode objects
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if parent_id:
            params['parent_id'] = parent_id
        if node_type:
            params['type'] = node_type
        
        response = self.client.get('/api/v2/vfs/nodes', params=params)
        data = response.json()
        return [VFSNode.from_dict(node) for node in data['nodes']]
    
    def get_node(self, node_id: str) -> VFSNode:
        """
        Get details for a specific VFS node.
        
        Args:
            node_id: VFS node UUID
            
        Returns:
            VFSNode object
        """
        response = self.client.get(f'/api/v2/vfs/nodes/{node_id}')
        data = response.json()
        return VFSNode.from_dict(data['node'])
    
    def upload_file(
        self,
        file: Union[str, BinaryIO],
        parent_id: Optional[str] = None,
        encrypt: bool = False
    ) -> VFSNode:
        """
        Upload a file to VFS.
        
        Args:
            file: File path or file-like object
            parent_id: Optional parent folder ID
            encrypt: Whether to encrypt the file
            
        Returns:
            VFSNode object for the uploaded file
        """
        # Prepare file for upload
        if isinstance(file, str):
            with open(file, 'rb') as f:
                file_data = {'file': (f.name, f.read())}
        else:
            file_data = {'file': file}
        
        # Prepare form data
        form_data = {'encrypt': str(encrypt).lower()}
        if parent_id:
            form_data['parent_id'] = parent_id
        
        response = self.client.post(
            '/api/v2/vfs/upload',
            files=file_data,
            data=form_data
        )
        data = response.json()
        return VFSNode.from_dict(data['node'])
    
    def download_file(self, node_id: str, output_path: Optional[str] = None) -> Union[bytes, str]:
        """
        Download a file from VFS.
        
        Args:
            node_id: VFS node UUID
            output_path: Optional path to save the file
            
        Returns:
            File content as bytes if no output_path, otherwise the saved file path
        """
        response = self.client.get(f'/api/v2/vfs/nodes/{node_id}/download', stream=True)
        
        if output_path:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return output_path
        else:
            return response.content
    
    def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None
    ) -> VFSNode:
        """
        Create a new folder in VFS.
        
        Args:
            name: Folder name
            parent_id: Optional parent folder ID
            
        Returns:
            VFSNode object for the created folder
        """
        data = {'name': name}
        if parent_id:
            data['parent_id'] = parent_id
        
        response = self.client.post('/api/v2/vfs/folders', data=data)
        result = response.json()
        return VFSNode.from_dict(result['folder'])
    
    def update_node(
        self,
        node_id: str,
        name: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> VFSNode:
        """
        Update a VFS node (rename or move).
        
        Args:
            node_id: VFS node UUID
            name: New name for the node
            parent_id: New parent folder ID
            
        Returns:
            Updated VFSNode object
        """
        data = {}
        if name is not None:
            data['name'] = name
        if parent_id is not None:
            data['parent_id'] = parent_id
        
        response = self.client.patch(f'/api/v2/vfs/nodes/{node_id}', data=data)
        result = response.json()
        return VFSNode.from_dict(result['node'])
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a VFS node (soft delete).
        
        Args:
            node_id: VFS node UUID
            
        Returns:
            True if deletion was successful
        """
        response = self.client.delete(f'/api/v2/vfs/nodes/{node_id}')
        data = response.json()
        return data.get('success', False)
    
    def get_folder_contents(self, folder_id: str) -> List[VFSNode]:
        """
        Get contents of a specific folder.
        
        Args:
            folder_id: Folder UUID
            
        Returns:
            List of VFSNode objects in the folder
        """
        return self.list_nodes(parent_id=folder_id)
    
    def search_files(
        self,
        name_pattern: Optional[str] = None,
        mime_type: Optional[str] = None,
        limit: int = 100
    ) -> List[VFSNode]:
        """
        Search for files by name pattern or MIME type.
        
        Args:
            name_pattern: Pattern to match in file names
            mime_type: MIME type to filter by
            limit: Number of results per page
            
        Returns:
            List of matching VFSNode objects
        """
        # Note: This would require additional API endpoints for search
        # For now, we'll list all files and filter client-side
        all_nodes = self.list_nodes(limit=limit)
        
        results = []
        for node in all_nodes:
            if node.type != 'file':
                continue
            
            if name_pattern and name_pattern.lower() not in node.name.lower():
                continue
            
            if mime_type and node.mime_type != mime_type:
                continue
            
            results.append(node)
        
        return results