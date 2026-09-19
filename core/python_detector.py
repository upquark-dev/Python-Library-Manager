"""Python Version Detector - Find all Python installations on the system"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Optional


class PythonVersion:
    """Represents a Python installation"""

    def __init__(self, path: str, version: str, is_venv: bool = False):
        self.path = path
        self.version = version
        self.is_venv = is_venv
        self.is_current = path == sys.executable

    def __str__(self):
        return f"Python {self.version} ({self.path})"

    def __repr__(self):
        return f"PythonVersion(path='{self.path}', version='{self.version}')"


class PythonDetector:
    """Detect all Python installations on the system"""

    def __init__(self):
        self.os_type = platform.system()
        self.found_pythons: List[PythonVersion] = []

    def detect_all(self) -> List[PythonVersion]:
        """Detect all Python installations"""
        self.found_pythons = []

        # Add current Python
        self._add_current_python()

        # Detect based on OS
        if self.os_type == "Windows":
            self._detect_windows()
        elif self.os_type == "Linux":
            self._detect_linux()
        elif self.os_type == "Darwin":  # macOS
            self._detect_macos()

        # Remove duplicates
        self._remove_duplicates()

        # Sort by version (newest first)
        self.found_pythons.sort(key=lambda p: p.version, reverse=True)

        return self.found_pythons

    def _add_current_python(self):
        """Add the current Python interpreter"""
        if getattr(sys, 'frozen', False):
            # Frozen exe: sys.executable is the app itself, not a Python.
            return
        try:
            version = self._get_python_version(sys.executable)
            if version:
                is_venv = hasattr(sys, 'real_prefix') or (
                    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
                )
                self.found_pythons.append(PythonVersion(sys.executable, version, is_venv))
        except Exception:
            pass

    def _detect_windows(self):
        """Detect Python installations on Windows"""

        # Check PATH
        self._check_path_commands(['python', 'python3', 'py'])

        # Check common installation directories
        common_paths = [
            Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'Python',
            Path(os.environ.get('PROGRAMFILES', '')) / 'Python',
            Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Python',
            Path('C:/Python'),
            Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'Programs' / 'Python',
        ]

        for base_path in common_paths:
            if base_path.exists():
                # Look for Python* directories
                try:
                    for python_dir in base_path.glob('Python*'):
                        python_exe = python_dir / 'python.exe'
                        if python_exe.exists():
                            version = self._get_python_version(str(python_exe))
                            if version:
                                self.found_pythons.append(PythonVersion(str(python_exe), version))
                except Exception:
                    pass

        # Check Windows Python Launcher
        try:
            result = subprocess.run(['py', '-0'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip().startswith('-'):
                        # Parse py launcher output
                        parts = line.split()
                        if len(parts) >= 2:
                            version_flag = parts[0].strip('-')
                            # Get path for this version
                            try:
                                path_result = subprocess.run(
                                    ['py', f'-{version_flag}', '-c', 'import sys; print(sys.executable)'],
                                    capture_output=True, text=True, timeout=5
                                )
                                if path_result.returncode == 0:
                                    python_path = path_result.stdout.strip()
                                    version = self._get_python_version(python_path)
                                    if version:
                                        self.found_pythons.append(PythonVersion(python_path, version))
                            except Exception:
                                pass
        except Exception:
            pass

    def _detect_linux(self):
        """Detect Python installations on Linux"""

        # Check PATH
        self._check_path_commands(['python', 'python3', 'python2'])

        # Check specific version commands
        for minor in range(6, 15):  # Python 3.6 to 3.14
            self._check_path_commands([f'python3.{minor}'])

        # Check common installation directories
        common_paths = [
            Path('/usr/bin'),
            Path('/usr/local/bin'),
            Path('/opt/python'),
            Path.home() / '.pyenv' / 'versions',
        ]

        for base_path in common_paths:
            if base_path.exists():
                try:
                    for python_exe in base_path.glob('python*'):
                        # Skip symlinks to avoid duplicates (we'll resolve them)
                        if python_exe.is_file() and os.access(python_exe, os.X_OK):
                            # Skip python-config and similar
                            if 'config' in python_exe.name or 'dbg' in python_exe.name:
                                continue
                            version = self._get_python_version(str(python_exe))
                            if version:
                                self.found_pythons.append(PythonVersion(str(python_exe), version))
                except Exception:
                    pass

        # Check pyenv installations
        pyenv_root = Path.home() / '.pyenv' / 'versions'
        if pyenv_root.exists():
            try:
                for version_dir in pyenv_root.iterdir():
                    python_exe = version_dir / 'bin' / 'python'
                    if python_exe.exists():
                        version = self._get_python_version(str(python_exe))
                        if version:
                            self.found_pythons.append(PythonVersion(str(python_exe), version))
            except Exception:
                pass

    def _detect_macos(self):
        """Detect Python installations on macOS"""

        # Check PATH
        self._check_path_commands(['python', 'python3', 'python2'])

        # Check specific version commands
        for minor in range(6, 15):
            self._check_path_commands([f'python3.{minor}'])

        # Check common installation directories
        common_paths = [
            Path('/usr/bin'),
            Path('/usr/local/bin'),
            Path('/opt/homebrew/bin'),
            Path('/Library/Frameworks/Python.framework/Versions'),
            Path.home() / 'Library' / 'Python',
        ]

        for base_path in common_paths:
            if base_path.exists():
                try:
                    for item in base_path.iterdir():
                        if item.is_dir() and item.name.replace('.', '').isdigit():
                            # Framework version directory
                            python_exe = item / 'bin' / 'python3'
                            if python_exe.exists():
                                version = self._get_python_version(str(python_exe))
                                if version:
                                    self.found_pythons.append(PythonVersion(str(python_exe), version))
                        elif item.is_file() and 'python' in item.name:
                            version = self._get_python_version(str(item))
                            if version:
                                self.found_pythons.append(PythonVersion(str(item), version))
                except Exception:
                    pass

    def _check_path_commands(self, commands: List[str]):
        """Check if commands are available in PATH"""
        for cmd in commands:
            try:
                result = subprocess.run(
                    [cmd, '-c', 'import sys; print(sys.executable)'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    python_path = result.stdout.strip()
                    version = self._get_python_version(python_path)
                    if version:
                        self.found_pythons.append(PythonVersion(python_path, version))
            except Exception:
                pass

    def _get_python_version(self, python_path: str) -> Optional[str]:
        """Get Python version for a given executable"""
        try:
            result = subprocess.run(
                [python_path, '--version'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Output is like "Python 3.10.5"
                version_line = result.stdout.strip() or result.stderr.strip()
                if 'Python' in version_line:
                    return version_line.replace('Python', '').strip()
        except Exception:
            pass
        return None

    def _remove_duplicates(self):
        """Remove duplicate Python installations"""
        seen_paths = set()
        unique_pythons = []

        for python in self.found_pythons:
            # Resolve symlinks
            try:
                real_path = os.path.realpath(python.path)
            except Exception:
                real_path = python.path

            if real_path not in seen_paths:
                seen_paths.add(real_path)
                unique_pythons.append(python)

        self.found_pythons = unique_pythons

    def get_python_info(self, python_path: str) -> Dict[str, str]:
        """Get detailed information about a Python installation"""
        try:
            result = subprocess.run(
                [python_path, '-c',
                 'import sys, platform; '
                 'print(f"{sys.version}|{platform.architecture()[0]}|{sys.prefix}")'
                ],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                return {
                    'version': parts[0] if len(parts) > 0 else 'Unknown',
                    'architecture': parts[1] if len(parts) > 1 else 'Unknown',
                    'prefix': parts[2] if len(parts) > 2 else 'Unknown',
                }
        except Exception:
            pass

        return {
            'version': 'Unknown',
            'architecture': 'Unknown',
            'prefix': 'Unknown',
        }
