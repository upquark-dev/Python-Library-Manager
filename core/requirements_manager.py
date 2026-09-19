"""Requirements.txt Manager - Import/Export requirements"""

import subprocess
import os
from typing import List, Tuple, Dict

from core.runtime import default_python_executable


class RequirementsManager:
    """Manages requirements.txt import/export"""

    def __init__(self, python_executable=None):
        self.python_executable = python_executable or default_python_executable()

    def export_requirements(self, file_path: str, include_versions: bool = True) -> Tuple[bool, str]:
        """
        Export installed packages to requirements.txt

        Args:
            file_path: Path to save requirements.txt
            include_versions: Include version numbers

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if include_versions:
                result = subprocess.run(
                    [self.python_executable, '-m', 'pip', 'freeze'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Get packages without versions
                result = subprocess.run(
                    [self.python_executable, '-m', 'pip', 'list', '--format', 'freeze'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Remove version numbers
                    lines = result.stdout.split('\n')
                    packages = [line.split('==')[0] for line in lines if line.strip()]
                    result.stdout = '\n'.join(packages)

            if result.returncode == 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                return True, f"Successfully exported to {file_path}"
            else:
                return False, result.stderr or "Failed to export requirements"

        except Exception as e:
            return False, str(e)

    def export_selected_packages(self, file_path: str, package_names: List[str],
                                 include_versions: bool = True) -> Tuple[bool, str]:
        """
        Export selected packages to requirements.txt

        Args:
            file_path: Path to save requirements.txt
            package_names: List of package names to export
            include_versions: Include version numbers

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            lines = []

            if include_versions:
                # Get all installed packages with versions
                result = subprocess.run(
                    [self.python_executable, '-m', 'pip', 'freeze'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    all_packages = result.stdout.split('\n')
                    package_dict = {}
                    for line in all_packages:
                        if '==' in line:
                            name, version = line.split('==', 1)
                            package_dict[name.lower()] = line

                    # Get selected packages
                    for pkg_name in package_names:
                        if pkg_name.lower() in package_dict:
                            lines.append(package_dict[pkg_name.lower()])
                        else:
                            lines.append(pkg_name)
            else:
                lines = package_names

            if lines:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                return True, f"Successfully exported {len(lines)} packages to {file_path}"
            else:
                return False, "No packages to export"

        except Exception as e:
            return False, str(e)

    def import_requirements(self, file_path: str) -> Tuple[bool, str]:
        """
        Install packages from requirements.txt

        Args:
            file_path: Path to requirements.txt

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            result = subprocess.run(
                [self.python_executable, '-m', 'pip', 'install', '-r', file_path],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return True, "Successfully installed packages from requirements.txt"
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, "Installation timeout"
        except Exception as e:
            return False, str(e)

    def parse_requirements_file(self, file_path: str) -> Tuple[bool, List[Dict]]:
        """
        Parse requirements.txt and return list of packages

        Args:
            file_path: Path to requirements.txt

        Returns:
            tuple: (success: bool, packages: List[Dict])
        """
        try:
            if not os.path.exists(file_path):
                return False, []

            packages = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package name and version
                        if '==' in line:
                            name, version = line.split('==', 1)
                            packages.append({
                                'name': name.strip(),
                                'version': version.strip(),
                                'line': line
                            })
                        elif '>=' in line:
                            name, version = line.split('>=', 1)
                            packages.append({
                                'name': name.strip(),
                                'version': f'>={version.strip()}',
                                'line': line
                            })
                        else:
                            packages.append({
                                'name': line,
                                'version': 'any',
                                'line': line
                            })

            return True, packages

        except Exception:
            return False, []

    def validate_requirements(self, file_path: str) -> Tuple[bool, str, List[str]]:
        """
        Validate requirements.txt file

        Args:
            file_path: Path to requirements.txt

        Returns:
            tuple: (valid: bool, message: str, errors: List[str])
        """
        try:
            if not os.path.exists(file_path):
                return False, "File not found", []

            errors = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Basic validation
                        if not any(op in line for op in ['==', '>=', '<=', '>', '<', '~=']):
                            if ' ' in line:
                                errors.append(f"Line {i}: Invalid format - '{line}'")

            if errors:
                return False, "Validation failed", errors
            else:
                return True, "Valid requirements file", []

        except Exception as e:
            return False, str(e), []

    def get_requirements_diff(self, file_path: str) -> Tuple[bool, Dict]:
        """
        Compare requirements.txt with installed packages

        Args:
            file_path: Path to requirements.txt

        Returns:
            tuple: (success: bool, diff: Dict with missing/extra/matching)
        """
        try:
            success, req_packages = self.parse_requirements_file(file_path)
            if not success:
                return False, {}

            # Get installed packages
            result = subprocess.run(
                [self.python_executable, '-m', 'pip', 'freeze'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return False, {}

            installed = {}
            for line in result.stdout.split('\n'):
                if '==' in line:
                    name, version = line.split('==', 1)
                    installed[name.lower()] = version

            req_names = {pkg['name'].lower() for pkg in req_packages}
            installed_names = set(installed.keys())

            diff = {
                'missing': list(req_names - installed_names),
                'extra': list(installed_names - req_names),
                'matching': list(req_names & installed_names)
            }

            return True, diff

        except Exception:
            return False, {}
