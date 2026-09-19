"""Virtual Environment Manager"""

import os
import platform
import shutil
import subprocess

from core.runtime import default_python_executable


class VirtualEnvManager:
    """Manages virtual environments"""

    def __init__(self):
        self.system = platform.system()
        self.python_executable = default_python_executable()

    def get_default_venv_path(self):
        """Get default path for virtual environments"""
        if self.system == "Windows":
            base = os.path.expanduser("~\\venvs")
        else:
            base = os.path.expanduser("~/venvs")

        os.makedirs(base, exist_ok=True)
        return base

    def list_venvs(self, base_path=None):
        """List all virtual environments in a directory"""
        if base_path is None:
            base_path = self.get_default_venv_path()

        venvs = []

        if not os.path.exists(base_path):
            return venvs

        for item in os.listdir(base_path):
            venv_path = os.path.join(base_path, item)
            if os.path.isdir(venv_path):
                # Check if it's a valid venv
                if self._is_valid_venv(venv_path):
                    venv_info = self._get_venv_info(venv_path)
                    venvs.append(venv_info)

        return venvs

    def _is_valid_venv(self, venv_path):
        """Check if directory is a valid virtual environment"""
        python_path = self.get_venv_python(venv_path)
        if self.system == "Windows":
            activate_path = os.path.join(venv_path, "Scripts", "activate.bat")
        else:
            activate_path = os.path.join(venv_path, "bin", "activate")

        return os.path.exists(python_path) and os.path.exists(activate_path)

    def _get_venv_info(self, venv_path):
        """Get information about a virtual environment"""
        info = {
            "name": os.path.basename(venv_path),
            "path": venv_path,
            "python_version": "Unknown",
            "package_count": 0,
            "size": "Unknown"
        }

        try:
            python_exe = self.get_venv_python(venv_path)

            result = subprocess.run(
                [python_exe, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info["python_version"] = result.stdout.strip().replace("Python ", "")

            # Get package count
            result = subprocess.run(
                [python_exe, "-m", "pip", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Count lines (minus 2 for header)
                lines = result.stdout.strip().split('\n')
                info["package_count"] = max(0, len(lines) - 2)

            # Get size
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(venv_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except OSError:
                        pass

            # Convert to MB
            size_mb = total_size / (1024 * 1024)
            info["size"] = f"{size_mb:.1f} MB"

        except Exception as e:
            info["error"] = str(e)

        return info

    def create_venv(self, name, path=None, python_version=None):
        """Create a new virtual environment"""
        if path is None:
            path = self.get_default_venv_path()

        venv_path = os.path.join(path, name)

        if os.path.exists(venv_path):
            return False, f"Virtual environment '{name}' already exists"

        try:
            # Use specified Python version or current
            python_cmd = python_version if python_version else self.python_executable

            # Create venv
            result = subprocess.run(
                [python_cmd, "-m", "venv", venv_path],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return True, f"Virtual environment '{name}' created successfully"
            else:
                return False, result.stderr

        except Exception as e:
            return False, str(e)

    def delete_venv(self, venv_path):
        """Delete a virtual environment"""
        try:
            if not os.path.exists(venv_path):
                return False, "Virtual environment does not exist"

            shutil.rmtree(venv_path)
            return True, "Virtual environment deleted successfully"

        except Exception as e:
            return False, str(e)

    def get_activate_command(self, venv_path):
        """Get the command to activate a virtual environment"""
        if self.system == "Windows":
            activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
            return activate_script
        else:
            activate_script = os.path.join(venv_path, "bin", "activate")
            return f"source {activate_script}"

    def install_in_venv(self, venv_path, package):
        """Install a package in a specific virtual environment"""
        try:
            if self.system == "Windows":
                pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
            else:
                pip_exe = os.path.join(venv_path, "bin", "pip")

            result = subprocess.run(
                [pip_exe, "install", package],
                capture_output=True,
                text=True,
                timeout=300
            )

            return result.returncode == 0, result.stdout + result.stderr

        except Exception as e:
            return False, str(e)

    def get_venv_python(self, venv_path):
        """Get Python executable path for a venv"""
        if self.system == "Windows":
            return os.path.join(venv_path, "Scripts", "python.exe")
        else:
            return os.path.join(venv_path, "bin", "python")
