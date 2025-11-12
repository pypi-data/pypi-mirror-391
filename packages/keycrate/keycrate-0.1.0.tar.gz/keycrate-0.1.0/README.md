# Keycrate Python SDK

License authentication SDK for Python projects.

## Installation

```bash
pip install keycrate
```

## Usage

### Authenticate with License Key

```python
from keycrate import configurate

client = configurate("https://api.keycrate.dev", "your-app-id")

result = client.authenticate(license="your-license-key")

if result["success"]:
    print("License verified!")
else:
    print("Error:", result["message"])
```

### Authenticate with Username/Password

```python
result = client.authenticate(
    username="user123",
    password="password123"
)
```

### Authenticate with HWID (Hardware ID)

```python
result = client.authenticate(
    license="your-license-key",
    hwid="device-id-12345"
)
```

### Register Credentials

```python
result = client.register(
    license="your-license-key",
    username="newuser@example.com",
    password="securepassword"
)

if result["success"]:
    print("Registration successful!")
else:
    print("Error:", result["message"])
```

## API Reference

### `configurate(host, app_id) -> LicenseAuthClient`

Factory function to create and configure a client.

**Parameters:**

-   `host` (str): Base URL of the Keycrate API
-   `app_id` (str): Your application ID

**Returns:** `LicenseAuthClient` instance

### `client.authenticate(license=None, username=None, password=None, hwid=None) -> dict`

Authenticate using either a license key or username/password.

**Parameters:**

-   `license` (str, optional): License key
-   `username` (str, optional): Username
-   `password` (str, optional): Password
-   `hwid` (str, optional): Hardware ID

**Returns:** Dictionary with `success` (bool), `message` (str), and optional `data`

**Raises:** `ValueError` if neither license nor username/password are provided

### `client.register(license, username, password) -> dict`

Register credentials for a license.

**Parameters:**

-   `license` (str, required): License key
-   `username` (str, required): Username
-   `password` (str, required): Password

**Returns:** Dictionary with `success` (bool), `message` (str), and optional `data`

## Response Structure

All methods return a dictionary:

```python
{
    "success": True,              # Operation succeeded
    "message": "Success message", # Response message
    "data": {...}                 # Optional response data
}
```

## Dependencies

-   `requests` - HTTP client library
