"""Dependency Manager"""

import subprocess
import re


def _clean_dep_name(dep):
    """Strip version specifiers from a dependency string, e.g. 'click>=8.0' -> 'click'"""
    return re.split(r'[<>=!]', dep)[0].strip()


class DependencyManager:
    """Manages package dependencies"""

    def _pip_show(self, package_name):
        """Run `pip show` for a package and return the CompletedProcess result"""
        return subprocess.run(
            ["pip", "show", package_name],
            capture_output=True,
            text=True,
            timeout=10
        )

    def get_package_dependencies(self, package_name):
        """Get dependencies of a package"""
        try:
            result = self._pip_show(package_name)

            if result.returncode != 0:
                return None, "Package not installed"

            dependencies = []
            for line in result.stdout.split('\n'):
                if line.startswith("Requires:"):
                    deps_str = line.split(":", 1)[1].strip()
                    if deps_str:
                        # Split by comma and clean up
                        dependencies = [d.strip() for d in deps_str.split(',')]
                    break

            return dependencies, None

        except Exception as e:
            return None, str(e)

    def get_reverse_dependencies(self, package_name):
        """Get packages that depend on this package"""
        try:
            result = self._pip_show(package_name)

            if result.returncode != 0:
                return None, "Package not installed"

            reverse_deps = []
            for line in result.stdout.split('\n'):
                if line.startswith("Required-by:"):
                    deps_str = line.split(":", 1)[1].strip()
                    if deps_str:
                        reverse_deps = [d.strip() for d in deps_str.split(',')]
                    break

            return reverse_deps, None

        except Exception as e:
            return None, str(e)

    def build_dependency_tree(self, package_name, max_depth=3, _current_depth=0, _visited=None):
        """Build a dependency tree for a package"""
        if _visited is None:
            _visited = set()

        if _current_depth >= max_depth or package_name in _visited:
            return None

        _visited.add(package_name)

        tree = {
            "name": package_name,
            "dependencies": [],
            "depth": _current_depth
        }

        deps, error = self.get_package_dependencies(package_name)

        if error or not deps:
            return tree

        for dep in deps:
            dep_clean = _clean_dep_name(dep)

            if dep_clean and dep_clean not in _visited:
                subtree = self.build_dependency_tree(
                    dep_clean,
                    max_depth,
                    _current_depth + 1,
                    _visited
                )
                if subtree:
                    tree["dependencies"].append(subtree)

        return tree

    def get_all_installed_packages(self):
        """Get list of all installed packages"""
        try:
            result = subprocess.run(
                ["pip", "list", "--format=freeze"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return []

            packages = []
            for line in result.stdout.split('\n'):
                if line.strip() and '==' in line:
                    package_name = line.split('==')[0].strip()
                    packages.append(package_name)

            return sorted(packages)

        except Exception:
            return []

    def find_circular_dependencies(self, package_name):
        """Find circular dependencies (if any)"""
        # This is a simplified version - full detection would be more complex
        visited = set()
        path = []
        circular = []

        def dfs(pkg):
            if pkg in path:
                # Found a cycle
                cycle_start = path.index(pkg)
                circular.append(path[cycle_start:] + [pkg])
                return

            if pkg in visited:
                return

            visited.add(pkg)
            path.append(pkg)

            deps, _ = self.get_package_dependencies(pkg)
            if deps:
                for dep in deps:
                    dep_clean = _clean_dep_name(dep)
                    if dep_clean:
                        dfs(dep_clean)

            path.pop()

        dfs(package_name)
        return circular

    def get_package_info_summary(self, package_name):
        """Get summary information about a package"""
        try:
            result = self._pip_show(package_name)

            if result.returncode != 0:
                return None

            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()

            return info

        except Exception:
            return None
