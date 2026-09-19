"""Package installation and management"""

import subprocess
import platform
import shlex
import re

from core.runtime import default_python_executable, is_frozen


class PackageInstaller:
    """Handles package installation and uninstallation across platforms"""

    def __init__(self):
        self.os_type = platform.system()
        self.python_executable = default_python_executable()

    def set_python_executable(self, python_path):
        """Set custom Python executable to use for package operations"""
        self.python_executable = python_path

    def get_python_info(self):
        """Get current Python executable and version"""
        if not self.python_executable:
            # Frozen build with no interpreter on PATH: report the embedded
            # runtime without spawning anything.
            return {
                'path': '(embedded)' if is_frozen() else '',
                'version': platform.python_version()
            }
        try:
            result = subprocess.run(
                [self.python_executable, '--version'],
                capture_output=True, text=True, timeout=5
            )
            version = result.stdout.strip() or result.stderr.strip()
            return {
                'path': self.python_executable,
                'version': version.replace('Python', '').strip()
            }
        except Exception:
            return {
                'path': self.python_executable,
                'version': 'Unknown'
            }

    def get_os_info(self):
        """Get detailed OS information"""
        os_name = platform.system()
        os_version = platform.version()
        os_release = platform.release()

        if os_name == "Windows":
            return f"Windows {os_release} ({os_version})"
        elif os_name == "Linux":
            try:
                with open("/etc/os-release") as f:
                    os_info = f.read()
                    name_match = re.search(r'PRETTY_NAME="([^"]+)"', os_info)
                    if name_match:
                        return name_match.group(1)
            except Exception:
                pass
            return f"Linux {os_release}"
        elif os_name == "Darwin":
            return f"macOS {os_release}"
        else:
            return f"{os_name} {os_release}"

    def install_package(self, install_cmd):
        """
        Install a package using the provided command

        Args:
            install_cmd: Installation command (e.g., "pip install numpy")

        Returns:
            tuple: (success: bool, output: str)
        """
        try:
            # Build argument list instead of shell string to avoid injection
            if install_cmd.startswith("pip "):
                args = [self.python_executable, '-m', 'pip'] + shlex.split(install_cmd[4:])
            else:
                args = shlex.split(install_cmd)

            # Run the installation command
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            output = result.stdout + result.stderr

            # Check if installation was successful
            if result.returncode == 0:
                return True, output
            else:
                return False, output

        except subprocess.TimeoutExpired:
            return False, "Error: Installation timed out after 5 minutes"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def uninstall_package(self, package_name):
        """
        Uninstall a package

        Args:
            package_name: Name of the package to uninstall

        Returns:
            tuple: (success: bool, output: str)
        """
        try:
            # Extract package name from complex names
            # For example: "PyQt6" from "PyQt6-WebEngine"
            # For most cases, take the first word
            base_package = package_name.split()[0].lower()

            # Use pip uninstall
            cmd = [self.python_executable, '-m', 'pip', 'uninstall', '-y', base_package]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                return True, output
            else:
                return False, output

        except subprocess.TimeoutExpired:
            return False, "Error: Uninstallation timed out"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def check_installed(self, package_name):
        """
        Check if a package is installed

        Args:
            package_name: Name of the package

        Returns:
            bool: True if installed, False otherwise
        """
        try:
            base_package = package_name.split()[0].lower()
            cmd = [self.python_executable, '-m', 'pip', 'show', base_package]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return result.returncode == 0
        except Exception:
            return False

    def upgrade_pip(self):
        """Upgrade pip to the latest version"""
        try:
            cmd = [self.python_executable, '-m', 'pip', 'install', '--upgrade', 'pip']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except Exception as e:
            return False, f"Error: {str(e)}"

    def list_installed(self):
        """List all installed packages"""
        try:
            cmd = [self.python_executable, '-m', 'pip', 'list']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except Exception as e:
            return False, f"Error: {str(e)}"
