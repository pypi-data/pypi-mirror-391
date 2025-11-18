# VPN Controller

Minimal OpenVPN connection manager for ProtonVPN - WSL-optimized.

Designed for Python developers who need VPN protection in their WSL scripts.

## Installation

```bash
pip install vpn-controller
```

## Setup

Create a `.env` file in your project directory:

```env
# ProtonVPN credentials (from account settings)
OPENVPN_USER="username+b1"
OPENVPN_PASS="password"

# OpenVPN config file (download from ProtonVPN)
OVPN_CONFIG="./config.ovpn"

# Path to OpenVPN executable on Windows
OPENVPN_EXE="/mnt/c/Program Files/OpenVPN/bin/openvpn.exe"

# Optional: Your country for connection validation
HOME_COUNTRY="Brazil"

# Optional: Connection timeout in seconds
CONNECT_TIMEOUT="15"
```

**Path formats supported:** Relative (`./file`), home (`~/file`), absolute (`/home/user/file`), Windows drives (`/mnt/c/...`)

## Quick Start

```python
from vpn_controller import VPNController

with VPNController() as vpn:
    if vpn.connect():
        print("Connected to VPN")
        # Your protected code here
    # Automatic disconnect on exit
```

## API Reference

### `VPNController`

Context manager for OpenVPN connection lifecycle.

#### Methods

##### `connect(force=False) -> bool`

Connects to VPN and validates the connection.

**Parameters:**
- `force` (bool): If `True`, kills any existing OpenVPN process before connecting. Default: `False`

**Returns:**
- `bool`: `True` if connected successfully, `False` otherwise

**Raises:**
- `RuntimeError`: Another VPN is running and `force=False`
- `FileNotFoundError`: OpenVPN executable or config file not found
- `ValueError`: Invalid or missing configuration in `.env`

**Example:**
```python
vpn = VPNController()

# Safe mode - fails if VPN already running
vpn.connect()

# Force mode - kills existing VPN first
vpn.connect(force=True)
```

##### `disconnect() -> bool`

Disconnects from VPN and cleans up resources (auth files, processes).

**Returns:**
- `bool`: Always returns `True`

**Example:**
```python
vpn.disconnect()
```

##### `is_connected() -> bool`

Checks if VPN is currently connected by validating IP geolocation.

**Returns:**
- `bool`: `True` if connected to VPN, `False` otherwise

**Example:**
```python
if vpn.is_connected():
    print("VPN is active")
```

#### Context Manager

Automatically disconnects on exit:

```python
with VPNController() as vpn:
    if vpn.connect():
        # Your code here
    # Automatic disconnect happens here
```

## Requirements

- **Python**: 3.6+
- **Platform**: WSL (Windows Subsystem for Linux)
- **Windows**: OpenVPN installed ([download](https://openvpn.net/community-downloads/))
- **Windows**: gsudo installed (`winget install gerardog.gsudo`)
- **Python packages**: `requests` (installed automatically via pip)
- **ProtonVPN**: Account with OpenVPN config file

---

**License:** MIT
