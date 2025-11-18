"""API client for Studio Manager API."""

import os
import requests
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError


class StudioManagerClient:
    """Client for Studio Manager API v2."""
    
    def __init__(self, api_url: Optional[str] = None, environment: str = 'dev'):
        """Initialize client.
        
        Args:
            api_url: Optional API URL (fetched from SSM if not provided)
            environment: Environment name (dev, sand, prod)
        """
        self.api_url = api_url
        self.environment = environment
        
        if not self.api_url:
            # Fetch from SSM Parameter Store
            ssm = boto3.client('ssm')
            param_name = f'/{environment}/studio-manager/api-url'
            try:
                param = ssm.get_parameter(Name=param_name)
                self.api_url = param['Parameter']['Value']
            except Exception as e:
                raise ValueError(
                    f"Could not fetch API URL from {param_name}. "
                    f"Set STUDIO_MANAGER_API_URL environment variable or pass api_url parameter. "
                    f"Error: {e}"
                )
    
    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API.
        
        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON
            
        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.api_url}{path}"
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # Engine operations
    def list_engines(self) -> Dict[str, Any]:
        """List all engines."""
        return self._request('GET', '/engines')
    
    def get_engine_readiness(self, engine_id: str) -> Dict[str, Any]:
        """Get engine readiness status with progress."""
        return self._request('GET', f'/engines/{engine_id}/readiness')
    
    def get_engine_status(self, engine_id: str) -> Dict[str, Any]:
        """Get comprehensive engine status including idle state."""
        return self._request('GET', f'/engines/{engine_id}')
    
    def launch_engine(self, name: str, user: str, engine_type: str, 
                     boot_disk_size: Optional[int] = None) -> Dict[str, Any]:
        """Launch a new engine."""
        payload = {
            'name': name,
            'user': user,
            'engine_type': engine_type
        }
        if boot_disk_size:
            payload['boot_disk_size'] = boot_disk_size
        return self._request('POST', '/engines', json=payload)
    
    def terminate_engine(self, engine_id: str) -> Dict[str, Any]:
        """Terminate an engine."""
        return self._request('DELETE', f'/engines/{engine_id}')
    
    def start_engine(self, engine_id: str) -> Dict[str, Any]:
        """Start a stopped engine."""
        return self._request('POST', f'/engines/{engine_id}/start')
    
    def stop_engine(self, engine_id: str) -> Dict[str, Any]:
        """Stop a running engine."""
        return self._request('POST', f'/engines/{engine_id}/stop')
    
    def resize_engine(self, engine_id: str, size_gb: int, online: bool = False) -> Dict[str, Any]:
        """Resize engine boot disk."""
        return self._request('POST', f'/engines/{engine_id}/resize', json={
            'size_gb': size_gb,
            'online': online
        })
    
    def create_ami(self, engine_id: str) -> Dict[str, Any]:
        """Create Golden AMI from engine."""
        return self._request('POST', f'/engines/{engine_id}/create-ami')
    
    def set_coffee(self, engine_id: str, duration: str) -> Dict[str, Any]:
        """Set coffee lock (keep-alive) for engine."""
        return self._request('POST', f'/engines/{engine_id}/coffee', json={
            'duration': duration
        })
    
    def cancel_coffee(self, engine_id: str) -> Dict[str, Any]:
        """Cancel coffee lock for engine."""
        return self._request('DELETE', f'/engines/{engine_id}/coffee')
    
    def update_idle_settings(self, engine_id: str, timeout: Optional[str] = None, 
                            slack: Optional[str] = None) -> Dict[str, Any]:
        """Update idle detector settings."""
        payload = {}
        if timeout:
            payload['timeout'] = timeout
        if slack:
            payload['slack'] = slack
        return self._request('PATCH', f'/engines/{engine_id}/idle-settings', json=payload)
    
    # Studio operations
    def list_studios(self) -> Dict[str, Any]:
        """List all studios."""
        return self._request('GET', '/studios')
    
    def get_studio(self, studio_id: str) -> Dict[str, Any]:
        """Get studio information."""
        return self._request('GET', f'/studios/{studio_id}')
    
    def create_studio(self, user: str, size_gb: int = 100) -> Dict[str, Any]:
        """Create a new studio."""
        return self._request('POST', '/studios', json={
            'user': user,
            'size_gb': size_gb
        })
    
    def delete_studio(self, studio_id: str) -> Dict[str, Any]:
        """Delete a studio."""
        return self._request('DELETE', f'/studios/{studio_id}')
    
    def resize_studio(self, studio_id: str, size_gb: int) -> Dict[str, Any]:
        """Resize a studio volume."""
        return self._request('POST', f'/studios/{studio_id}/resize', json={
            'size_gb': size_gb
        })
    
    def reset_studio(self, studio_id: str) -> Dict[str, Any]:
        """Reset a stuck studio to available status."""
        return self._request('POST', f'/studios/{studio_id}/reset')
    
    # Attachment operations
    def attach_studio(self, studio_id: str, engine_id: str, user: str) -> Dict[str, Any]:
        """Initiate studio attachment."""
        return self._request('POST', f'/studios/{studio_id}/attach', json={
            'engine_id': engine_id,
            'user': user
        })
    
    def detach_studio(self, studio_id: str) -> Dict[str, Any]:
        """Detach a studio."""
        return self._request('POST', f'/studios/{studio_id}/detach')
    
    def get_attachment_progress(self, operation_id: str) -> Dict[str, Any]:
        """Get attachment operation progress."""
        return self._request('GET', f'/operations/{operation_id}')
    
    # Helper methods
    def check_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Check EC2 instance status including status checks.
        
        Args:
            instance_id: EC2 instance ID
            
        Returns:
            Dict with:
                - state: Instance state (pending, running, etc.)
                - instance_status: Instance status check (initializing, ok, impaired)
                - system_status: System status check (initializing, ok, impaired)
                - reachable: True if both status checks passed
        """
        ec2 = boto3.client('ec2')
        
        try:
            # Get instance state
            instances_resp = ec2.describe_instances(InstanceIds=[instance_id])
            if not instances_resp['Reservations']:
                return {'error': 'Instance not found'}
            
            instance = instances_resp['Reservations'][0]['Instances'][0]
            state = instance['State']['Name']
            
            # Get status checks (only available when running)
            if state != 'running':
                return {
                    'state': state,
                    'instance_status': None,
                    'system_status': None,
                    'reachable': False
                }
            
            # Fetch instance status checks
            status_resp = ec2.describe_instance_status(
                InstanceIds=[instance_id],
                IncludeAllInstances=False  # Only get running instances
            )
            
            if not status_resp['InstanceStatuses']:
                # No status yet - still initializing
                return {
                    'state': state,
                    'instance_status': 'initializing',
                    'system_status': 'initializing',
                    'reachable': False
                }
            
            status = status_resp['InstanceStatuses'][0]
            instance_status = status['InstanceStatus']['Status']
            system_status = status['SystemStatus']['Status']
            
            return {
                'state': state,
                'instance_status': instance_status,
                'system_status': system_status,
                'reachable': instance_status == 'ok' and system_status == 'ok'
            }
            
        except ClientError as e:
            return {'error': str(e)}
    
    def get_engine_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find engine by name.
        
        Args:
            name: Engine name
            
        Returns:
            Engine dict or None if not found
        """
        engines = self.list_engines().get('engines', [])
        for engine in engines:
            if engine['name'] == name:
                return engine
        return None
    
    def get_my_studio(self) -> Optional[Dict[str, Any]]:
        """Get current user's studio.
        
        Returns:
            Studio dict or None if not found
            
        Raises:
            RuntimeError: If not authenticated to AWS
        """
        from .auth import get_aws_username
        
        user = get_aws_username()
        
        studios = self.list_studios().get('studios', [])
        for studio in studios:
            if studio['user'] == user:
                return studio
        return None


