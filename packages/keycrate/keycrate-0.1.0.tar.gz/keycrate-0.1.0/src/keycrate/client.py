import requests
from typing import Optional, Dict, Any


class LicenseAuthClient:
    """Client for license authentication and registration"""
    
    def __init__(self, host: str, app_id: str):
        """
        Initialize the client.
        
        Args:
            host: Base URL of the API (e.g., 'https://api.example.com')
            app_id: Application ID for authentication
        """
        self.host = host.rstrip('/')
        self.app_id = app_id

    def authenticate(
        self,
        license: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        hwid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate using either a license key or username/password combination.
        
        Args:
            license: License key for authentication
            username: Username for authentication
            password: Password for authentication
            hwid: Hardware ID (optional, required for HWID-locked licenses)
        
        Returns:
            Dict with 'success' (bool) and 'message' (str), plus optional 'data'
        
        Raises:
            ValueError: If neither license nor username/password are provided
        """
        # Validate authentication method
        if not license and not (username and password):
            return {
                "success": False,
                "message": "Either license key OR (username AND password) must be provided"
            }
        
        url = f"{self.host}/auth"
        payload = {"app_id": self.app_id}

        if license:
            payload["license"] = license
        if username:
            payload["username"] = username
        if password:
            payload["password"] = password
        if hwid:
            payload["hwid"] = hwid

        try:
            response = requests.post(url, json=payload, timeout=10)
            try:
                return response.json()
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid response from server (HTTP {response.status_code})"
                }
        except requests.RequestException as e:
            return {"success": False, "message": f"Request failed: {str(e)}"}

    def register(
        self,
        license: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Register credentials for a license.
        
        Args:
            license: License key (REQUIRED)
            username: Username (REQUIRED)
            password: Password (REQUIRED)
        
        Returns:
            Dict with 'success' (bool) and 'message' (str)
        
        Raises:
            ValueError: If any required field is missing
        """
        # Validate all required fields
        if not license:
            return {"success": False, "message": "license is required"}
        if not username:
            return {"success": False, "message": "username is required"}
        if not password:
            return {"success": False, "message": "password is required"}

        url = f"{self.host}/register"
        payload = {
            "app_id": self.app_id,
            "license": license,
            "username": username,
            "password": password
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            try:
                return response.json()
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid response from server (HTTP {response.status_code})"
                }
        except requests.RequestException as e:
            return {"success": False, "message": f"Request failed: {str(e)}"}


def configurate(host: str, app_id: str) -> LicenseAuthClient:
    """
    Factory function to create and configure a client.
    
    Args:
        host: Base URL of the API
        app_id: Application ID
    
    Returns:
        Configured LicenseAuthClient instance
    """
    return LicenseAuthClient(host, app_id)