"""Bulk Update Manager - Check and update packages"""

import json
import re
import subprocess
from typing import List, Dict, Tuple

from core.runtime import default_python_executable


class UpdateManager:
    """Manages package updates"""

    def __init__(self, python_executable=None):
        self.python_executable = python_executable or default_python_executable()

    def check_outdated_packages(self) -> Tuple[bool, List[Dict]]:
        """
        Check for outdated packages

        Returns:
            tuple: (success: bool, packages: List[Dict])
        """
        try:
            result = subprocess.run(
                [self.python_executable, '-m', 'pip', 'list', '--outdated', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return True, packages
            else:
                return False, []

        except Exception:
            return False, []

    def update_package(self, package_name: str, mirror_url: str = None) -> Tuple[bool, str]:
        """
        Update a single package

        Args:
            package_name: Name of the package to update
            mirror_url: Optional mirror URL for faster downloads in China

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            cmd = [self.python_executable, '-m', 'pip', 'install', '--upgrade', package_name]
            if mirror_url:
                cmd.extend(['-i', mirror_url])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return True, f"Successfully updated {package_name}"
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, f"Update timeout for {package_name}"
        except Exception as e:
            return False, str(e)

    def update_multiple_packages(self, package_names: List[str], mirror_url: str = None) -> List[Dict]:
        """
        Update multiple packages

        Args:
            package_names: List of package names to update
            mirror_url: Optional mirror URL for faster downloads in China

        Returns:
            list: Results for each package
        """
        results = []

        for package_name in package_names:
            success, message = self.update_package(package_name, mirror_url)
            results.append({
                'package': package_name,
                'success': success,
                'message': message
            })

        return results

    def update_all_outdated(self, mirror_url: str = None) -> Tuple[bool, str]:
        """
        Update all outdated packages at once

        Args:
            mirror_url: Optional mirror URL for faster downloads in China

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Get list of outdated packages
            success, outdated = self.check_outdated_packages()

            if not success or not outdated:
                return True, "No packages to update"

            package_names = [pkg['name'] for pkg in outdated]

            # Update all at once
            cmd = [self.python_executable, '-m', 'pip', 'install', '--upgrade'] + package_names
            if mirror_url:
                cmd.extend(['-i', mirror_url])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return True, f"Successfully updated {len(package_names)} packages"
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, "Update timeout"
        except Exception as e:
            return False, str(e)

    def get_package_latest_version(self, package_name: str) -> str:
        """
        Get latest version of a package from PyPI

        Args:
            package_name: Name of the package

        Returns:
            str: Latest version or 'Unknown'
        """
        try:
            result = subprocess.run(
                [self.python_executable, '-m', 'pip', 'index', 'versions', package_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse output to get latest version
                for line in result.stdout.split('\n'):
                    if 'Available versions:' in line or 'LATEST:' in line:
                        versions = re.findall(r'\d+\.\d+\.\d+', line)
                        if versions:
                            return versions[0]

            return 'Unknown'

        except Exception:
            return 'Unknown'
