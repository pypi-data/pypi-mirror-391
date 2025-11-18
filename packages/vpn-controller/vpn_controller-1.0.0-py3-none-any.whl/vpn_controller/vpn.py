"""OpenVPN connection manager for ProtonVPN - Hybrid Windows/WSL version"""

import subprocess
import tempfile
import os
import sys
import time
import requests
import platform
import re
from pathlib import Path


class VPNController:
    """Manages OpenVPN connections with automatic cleanup (Windows/WSL hybrid)"""

    def __init__(self):
        self._process = None
        self._auth_file = None
        self._platform = 'wsl'  # Assume WSL only
        # Cache distro name to avoid reading /etc/os-release on every path conversion
        self._distro_name = self._get_distro_name()
        # Load .env once during initialization
        self._env = self._load_env()

    def _get_distro_name(self):
        """
        Get the WSL distribution name (cached in __init__).

        Returns:
            str: Distribution name (e.g., 'Ubuntu', 'Debian', 'Ubuntu-20.04')
        """
        # Try to get from WSL_DISTRO_NAME environment variable first
        distro = os.environ.get('WSL_DISTRO_NAME')
        if distro:
            return distro

        # Fallback: try to detect from /etc/os-release
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        distro_id = line.split('=')[1].strip().strip('"')
                        # Capitalize first letter for common distros
                        return distro_id.capitalize()
        except (FileNotFoundError, PermissionError):
            pass

        # Default fallback
        return 'Ubuntu'

    def _load_env(self):
        env_file = Path(__file__).parent / '.env'
        if not env_file.exists():
            raise FileNotFoundError(".env file not found")

        env = {}
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    env[key] = val.strip('"').strip("'")
        return env

    def _expand_path(self, path):
        """
        Expand user input path to absolute WSL path.
        Handles: ./, ~, and absolute paths

        Args:
            path: User-provided path (./file, ~/file, /abs/path)

        Returns:
            str: Absolute WSL path

        Raises:
            ValueError: If path is None or empty
        """
        # Validate path
        if path is None:
            raise ValueError("Path cannot be None")

        # Strip whitespace
        path = path.strip()

        if not path:
            raise ValueError("Path cannot be empty")

        # Expand ~ to home directory
        if path.startswith('~'):
            path = os.path.expanduser(path)

        # Convert relative to absolute
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        return path

    def _to_windows_path(self, wsl_path):
        """
        Convert WSL path to Windows path for openvpn.exe.

        Args:
            wsl_path: Absolute WSL path

        Returns:
            str: Windows-format path

        Examples:
            /mnt/c/Users/foo/file.ovpn -> C:\\Users\\foo\\file.ovpn
            /tmp/auth.txt -> \\\\wsl$\\Ubuntu\\tmp\\auth.txt
        """
        # Handle /mnt/c/ style paths
        if wsl_path.startswith('/mnt/'):
            # /mnt/c/Users/... -> C:\Users\...
            parts = wsl_path.split('/')
            if len(parts) >= 3:
                drive_letter = parts[2].upper()
                remaining_path = '/'.join(parts[3:])
                return f"{drive_letter}:\\{remaining_path.replace('/', '\\')}"

        # Handle native WSL paths -> \\wsl$\distro\path
        # Use cached distro name
        distro_name = self._distro_name if self._distro_name else "Ubuntu"

        # Convert /path -> \\wsl$\Ubuntu\path
        win_path = wsl_path.replace('/', '\\')
        return f"\\\\wsl$\\{distro_name}{win_path}"

    def _validate_connection(self, home_country):
        try:
            r = requests.get('http://ip-api.com/json/', timeout=5)
            return r.json().get('country') != home_country
        except (requests.RequestException, ValueError, KeyError):
            return False

    def _check_existing_openvpn(self):
        """
        Check if there's already an OpenVPN process running.

        Returns:
            tuple: (bool, str) - (is_running, process_info)
        """
        if self._platform != 'wsl':
            # Only implemented for WSL currently
            return False, ""

        try:
            result = subprocess.run(
                ['cmd.exe', '/c', 'tasklist', '|', 'findstr', '/I', 'openvpn.exe'],
                capture_output=True,
                text=True,
                encoding='cp1252',
                errors='replace',
                timeout=5
            )

            # If openvpn.exe is found (not just services)
            if result.returncode == 0 and 'openvpn.exe' in result.stdout.lower():
                # Filter out service processes, only report client processes
                lines = [line.strip() for line in result.stdout.split('\n') 
                         if 'openvpn.exe' in line.lower() and 'serv' not in line.lower()]
                if lines:
                    return True, '\n'.join(lines)

            return False, ""

        except Exception:
            # If we can't check, assume it's safe to proceed
            return False, ""

    def connect(self, force=False):
        """
        Connect to VPN using OpenVPN (Windows/WSL hybrid).

        Args:
            force (bool): If True, automatically disconnect any existing OpenVPN
                         connections before connecting. If False (default), raise
                         an error if another VPN is already running.

        Returns:
            bool: True if connected successfully, False otherwise

        Raises:
            RuntimeError: If another VPN is running and force=False
            FileNotFoundError: If required files are not found

        Example:
            # Safe mode - fails if VPN already running
            vpn.connect()

            # Force mode - kills existing VPN and connects
            vpn.connect(force=True)
        """
        # Normalize paths based on platform
        config_path_raw = self._env['OVPN_CONFIG']
        openvpn_exe_raw = self._env['OPENVPN_EXE']

        config_path = self._expand_path(config_path_raw)
        openvpn_exe = self._expand_path(openvpn_exe_raw)

        username = self._env['OPENVPN_USER']
        password = self._env['OPENVPN_PASS']
        timeout = int(self._env.get('CONNECT_TIMEOUT', 15))
        home_country = self._env.get('HOME_COUNTRY', 'Brazil')

        # Verify files exist
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if not os.path.exists(openvpn_exe):
            raise FileNotFoundError(f"OpenVPN not found: {openvpn_exe}")

        # Check if there's already an OpenVPN process running
        is_running, process_info = self._check_existing_openvpn()
        if is_running:
            if force:
                # Automatically disconnect existing VPN
                self.disconnect()
                # Wait a moment for cleanup
                time.sleep(1)
            else:
                raise RuntimeError(
                    f"Another OpenVPN instance is already running.\n"
                    f"Please disconnect it first or use connect(force=True):\n{process_info}"
                )

        # Create auth file in /tmp (WSL)
        self._auth_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', dir='/tmp')
        self._auth_file.write(f"{username}\n{password}")
        self._auth_file.close()
        # Convert WSL temp path to Windows path for OpenVPN
        auth_file_path = self._to_windows_path(self._auth_file.name)

        # Prepare subprocess arguments (WSL only)
        kwargs = {
            'stdout': subprocess.DEVNULL,
            'stderr': subprocess.PIPE,
            'text': True,
            'encoding': 'cp1252',
            'errors': 'replace'
        }

        # Convert paths to Windows format for openvpn.exe
        config_path_win = self._to_windows_path(config_path)
        openvpn_exe_win = self._to_windows_path(openvpn_exe)

        # Launch OpenVPN with gsudo elevation (WSL only)
        try:
            # Find gsudo
            gsudo_path = "/mnt/c/Program Files/gsudo/Current/gsudo.exe"
            if not os.path.exists(gsudo_path):
                # Fallback to PATH (WinGet install location)
                gsudo_path = "gsudo"

            # Build command with Windows paths
            cmd = [gsudo_path, openvpn_exe_win, '--config', config_path_win, '--auth-user-pass', auth_file_path]

            self._process = subprocess.Popen(cmd, **kwargs)

            # Check if process failed immediately (within 1 second)
            time.sleep(1)
            poll_result = self._process.poll()
            if poll_result is not None:
                # Process terminated - read stderr
                try:
                    _, stderr = self._process.communicate(timeout=2)
                    error_msg = f"OpenVPN process terminated immediately (exit code {poll_result})"
                    if stderr and stderr.strip():
                        error_msg += f"\nError output: {stderr.strip()}"
                    raise RuntimeError(error_msg)
                except subprocess.TimeoutExpired:
                    raise RuntimeError(f"OpenVPN process terminated immediately (exit code {poll_result})")
        except Exception as e:
            # Clean up auth file on error
            if self._auth_file:
                try:
                    os.unlink(self._auth_file.name)
                except OSError:
                    pass
                self._auth_file = None
            raise RuntimeError(f"Failed to start OpenVPN: {e}")

        # Optimized validation: check every 2 seconds instead of 1
        check_interval = 2
        for _ in range(timeout // check_interval):
            time.sleep(check_interval)
            if self._validate_connection(home_country):
                return True

        self.disconnect()
        return False

    def disconnect(self):
        """
        Disconnect from VPN and clean up resources.
        
        This method kills all OpenVPN client processes, not just the one we started,
        to ensure the VPN is actually disconnected even if our process tracking failed.

        Returns:
            bool: Always returns True
        """
        # First, try to terminate our tracked process
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            except Exception:
                pass  # Process may already be dead
            finally:
                self._process = None

        # Kill ALL OpenVPN client processes (not service processes)
        # This ensures we disconnect even if our process tracking failed
        if self._platform == 'wsl':
            try:
                # Find gsudo for elevated taskkill
                gsudo_paths = [
                    "/mnt/c/Program Files/gsudo/Current/gsudo.exe",
                    "/mnt/c/Program Files/gsudo/2.6.1/gsudo.exe",
                    f"/mnt/c/Users/{os.environ.get('USER')}/AppData/Local/Microsoft/WinGet/Links/gsudo.exe"
                ]
                gsudo_path = None
                for path in gsudo_paths:
                    if os.path.exists(path):
                        gsudo_path = path
                        break

                # Find all openvpn.exe client processes (exclude services)
                result = subprocess.run(
                    ['cmd.exe', '/c', 'tasklist', '/FI', 'IMAGENAME eq openvpn.exe', '/FO', 'CSV', '/NH'],
                    capture_output=True,
                    text=True,
                    encoding='cp1252',
                    errors='replace',
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout:
                    # Parse CSV output to get PIDs
                    import csv
                    from io import StringIO
                    
                    reader = csv.reader(StringIO(result.stdout))
                    for row in reader:
                        if len(row) >= 2 and 'openvpn.exe' in row[0].lower():
                            # row[0] = image name, row[1] = PID, row[2] = session type
                            # Skip service processes (they run as Services, not Console)
                            if len(row) >= 3 and 'console' in row[2].lower():
                                try:
                                    pid = row[1].strip().strip('"')
                                    # Use gsudo for elevated taskkill if available
                                    if gsudo_path:
                                        subprocess.run(
                                            [gsudo_path, 'taskkill', '/F', '/PID', pid],
                                            capture_output=True,
                                            timeout=5
                                        )
                                    else:
                                        # Fallback to direct taskkill (may fail without admin)
                                        subprocess.run(
                                            ['cmd.exe', '/c', 'taskkill', '/F', '/PID', pid],
                                            capture_output=True,
                                            timeout=5
                                        )
                                except Exception:
                                    pass  # Best effort
            except Exception:
                pass  # Best effort cleanup

        # Clean up auth file
        if self._auth_file:
            try:
                os.unlink(self._auth_file.name)
            except OSError:
                pass
            self._auth_file = None

        return True

    def is_connected(self):
        """
        Check if VPN connection is active.

        Returns:
            bool: True if connected, False otherwise
        """
        if not self._process or self._process.poll() is not None:
            return False

        home_country = self._env.get('HOME_COUNTRY', 'Brazil')
        return self._validate_connection(home_country)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.disconnect()
        return False

