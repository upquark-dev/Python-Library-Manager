"""Package Version Manager"""

import subprocess
from packaging import version


class PackageVersionManager:
    """Manages package versions"""

    def get_available_versions(self, package_name):
        """Get all available versions of a package from PyPI"""
        try:
            # Use pip index versions command
            result = subprocess.run(
                ["pip", "index", "versions", package_name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return [], "Package not found or error connecting to PyPI"

            # Parse output
            versions = []
            output = result.stdout

            # Look for "Available versions:" section
            if "Available versions:" in output:
                version_line = output.split("Available versions:")[1].split("\n")[0]
                # Split by comma and clean up
                version_strings = version_line.split(",")
                for v in version_strings:
                    v = v.strip()
                    if v:
                        versions.append(v)

            return versions, None

        except subprocess.TimeoutExpired:
            return [], "Request timed out"
        except Exception as e:
            return [], str(e)

    def get_installed_version(self, package_name):
        """Get currently installed version of a package"""
        try:
            result = subprocess.run(
                ["pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse version from output
                for line in result.stdout.split('\n'):
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()

            return None

        except Exception:
            return None

    def install_specific_version(self, package_name, version_str):
        """Install a specific version of a package"""
        try:
            package_spec = f"{package_name}=={version_str}"

            result = subprocess.run(
                ["pip", "install", package_spec],
                capture_output=True,
                text=True,
                timeout=300
            )

            return result.returncode == 0, result.stdout + result.stderr

        except Exception as e:
            return False, str(e)

    def get_latest_version(self, package_name):
        """Get the latest version available"""
        versions, error = self.get_available_versions(package_name)

        if error or not versions:
            return None

        # First entry reported by pip is the latest version
        return versions[0]

    def compare_versions(self, ver1, ver2):
        """Compare two version strings"""
        try:
            v1 = version.parse(ver1)
            v2 = version.parse(ver2)

            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
            else:
                return 0
        except Exception:
            return 0

    def sort_versions(self, versions_list):
        """Sort versions in descending order (latest first)"""
        try:
            sorted_versions = sorted(
                versions_list,
                key=lambda v: version.parse(v),
                reverse=True
            )
            return sorted_versions
        except Exception:
            return versions_list
