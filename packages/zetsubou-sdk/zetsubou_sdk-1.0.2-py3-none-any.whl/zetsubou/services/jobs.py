"""
Jobs Service

Handles job management, status checking, and result retrieval.
"""

from typing import List, Dict, Any, Optional, BinaryIO, Union
from ..models import Job
from ..exceptions import ZetsubouError


class JobsService:
    """Service for managing jobs and job results."""
    
    def __init__(self, client):
        self.client = client
    
    def list(
        self,
        status: Optional[str] = None,
        tool_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Job]:
        """
        List jobs with optional filtering.
        
        Args:
            status: Filter by job status (pending, running, completed, failed, cancelled)
            tool_id: Filter by tool ID
            limit: Number of results per page
            offset: Pagination offset
            
        Returns:
            List of Job objects
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if status:
            params['status'] = status
        if tool_id:
            params['tool_id'] = tool_id
        
        response = self.client.get('/api/v2/jobs', params=params)
        data = response.json()
        return [Job.from_dict(job) for job in data['jobs']]
    
    def get(self, job_id: str) -> Job:
        """
        Get details for a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job object
        """
        response = self.client.get(f'/api/v2/jobs/{job_id}')
        data = response.json()
        return Job.from_dict(data['job'])
    
    def wait_for_completion(
        self,
        job_id: str,
        timeout: int = 3600,
        poll_interval: int = 5
    ) -> Job:
        """
        Wait for a job to complete with polling.
        
        Args:
            job_id: Job identifier
            timeout: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds
            
        Returns:
            Completed Job object
            
        Raises:
            ZetsubouError: If job fails or times out
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job = self.get(job_id)
            
            if job.status == 'completed':
                return job
            elif job.status == 'failed':
                raise ZetsubouError(f"Job {job_id} failed: {job.error}")
            elif job.status == 'cancelled':
                raise ZetsubouError(f"Job {job_id} was cancelled")
            
            time.sleep(poll_interval)
        
        raise ZetsubouError(f"Job {job_id} timed out after {timeout} seconds")
    
    def cancel(self, job_id: str) -> bool:
        """
        Cancel a running job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancellation was successful
        """
        response = self.client.post(f'/api/v2/jobs/{job_id}/cancel')
        data = response.json()
        return data.get('success', False)
    
    def retry(self, job_id: str) -> Job:
        """
        Retry a failed job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            New Job object
        """
        response = self.client.post(f'/api/v2/jobs/{job_id}/retry')
        data = response.json()
        return Job.from_dict(data['job'])
    
    def delete(self, job_id: str) -> bool:
        """
        Delete a job and free its storage.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if deletion was successful
        """
        response = self.client.delete(f'/api/v2/jobs/{job_id}')
        data = response.json()
        return data.get('success', False)
    
    def download_results(self, job_id: str, output_path: Optional[str] = None) -> Union[bytes, str]:
        """
        Download job results as a ZIP file.
        
        Args:
            job_id: Job identifier
            output_path: Optional path to save the file
            
        Returns:
            File content as bytes if no output_path, otherwise the saved file path
        """
        response = self.client.get(f'/api/v2/jobs/{job_id}/download', stream=True)
        
        if output_path:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return output_path
        else:
            return response.content
    
    def get_progress(self, job_id: str) -> Dict[str, Any]:
        """
        Get job progress information.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Progress information
        """
        job = self.get(job_id)
        return {
            'status': job.status,
            'progress': job.progress,
            'error': job.error,
            'created_at': job.created_at,
            'updated_at': job.updated_at,
            'completed_at': job.completed_at
        }