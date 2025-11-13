"""
Main Cortefy client class
"""
import requests
from typing import Optional
from .exceptions import AuthenticationError, APIError, ValidationError
from .resources import MemoriesResource, SearchResource


class Cortefy:
    """
    Main client for interacting with the Cortefy API
    
    Usage:
        from cortefy import Cortefy
        import os
        
        client = Cortefy(
            api_key=os.environ.get("CORTEFY_API_KEY"),
            base_url="https://api.cortefy.com"  # optional
        )
        
        result = client.memories.add(
            content="Machine learning enables computers to learn from data",
            container_tags=["ai-research"],
            metadata={"priority": "high"}
        )
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None
    ):
        """
        Initialize the Cortefy client
        
        Args:
            api_key: Your Cortefy API key
            base_url: Base URL for the API (defaults to http://localhost:8000 for local dev)
        """
        if not api_key:
            raise ValueError("api_key is required")
        
        self.api_key = api_key
        self.base_url = base_url or "http://localhost:8000"
        
        # Remove trailing slash if present
        self.base_url = self.base_url.rstrip('/')
        
        # Initialize resources
        self.memories = MemoriesResource(self)
        self.search = SearchResource(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """
        Make an HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., '/api/memories/ingest/')
            json: JSON body for the request
            params: Query parameters
            
        Returns:
            Response JSON as dict
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API returns an error
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                params=params,
                timeout=30
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            
            # Handle validation errors (400)
            if response.status_code == 400:
                error_msg = "Validation error"
                try:
                    error_data = response.json()
                    # Extract validation error message from DRF format
                    if isinstance(error_data, dict):
                        # DRF returns errors like {"field": ["error message"]}
                        error_messages = []
                        for field, messages in error_data.items():
                            if isinstance(messages, list):
                                error_messages.extend(messages)
                            else:
                                error_messages.append(str(messages))
                        if error_messages:
                            error_msg = "; ".join(error_messages)
                        elif "error" in error_data:
                            error_msg = error_data["error"]
                except:
                    error_msg = response.text or "Validation error"
                
                raise ValidationError(error_msg)
            
            # Handle other errors
            if not response.ok:
                error_msg = "API request failed"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                
                raise APIError(
                    error_msg,
                    status_code=response.status_code,
                    response=response
                )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def _request_file(
        self,
        method: str,
        endpoint: str,
        files: dict,
        data: Optional[dict] = None
    ) -> dict:
        """
        Make an HTTP request with file upload
        
        Args:
            method: HTTP method (POST, etc.)
            endpoint: API endpoint path
            files: Dictionary of files to upload (e.g., {'file': (filename, file_obj)})
            data: Form data to send
            
        Returns:
            Response JSON as dict
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API returns an error
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                files=files,
                data=data or {},
                timeout=120  # Longer timeout for file uploads
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            
            # Handle validation errors (400)
            if response.status_code == 400:
                error_msg = "Validation error"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_messages = []
                        for field, messages in error_data.items():
                            if isinstance(messages, list):
                                error_messages.extend(messages)
                            else:
                                error_messages.append(str(messages))
                        if error_messages:
                            error_msg = "; ".join(error_messages)
                        elif "error" in error_data:
                            error_msg = error_data["error"]
                except:
                    error_msg = response.text or "Validation error"
                
                raise ValidationError(error_msg)
            
            # Handle other errors
            if not response.ok:
                error_msg = "API request failed"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                
                raise APIError(
                    error_msg,
                    status_code=response.status_code,
                    response=response
                )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

