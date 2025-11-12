"""
Core dependency detection and analysis module
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

try:
    from importlib.metadata import distributions, distribution, PackageNotFoundError
except ImportError:
    from importlib_metadata import distributions, distribution, PackageNotFoundError

from ..utils.helpers import (
    get_environment_type, get_pip_list, normalize_package_name
)

class DependencyDetector:
    """
    Intelligent dependency detection that distinguishes between
    primary packages and their auto-installed dependencies.
    """

    def __init__(self, environment_path: Optional[str] = None):
        self.environment_path = environment_path
        self.env_type = get_environment_type()
        self._dependency_graph = {}

        # Common packages that are usually dependencies, not primary
        self.common_dependencies = {
            'pip', 'setuptools', 'wheel', 'distlib', 'packaging', 'six',
            'certifi', 'charset-normalizer', 'idna', 'urllib3', 'requests-oauthlib',
            'pyasn1', 'pyasn1-modules', 'rsa', 'cachetools', 'google-auth',
            'pyparsing', 'cycler', 'kiwisolver', 'python-dateutil', 'pytz',
            'markupsafe', 'itsdangerous', 'blinker', 'importlib-metadata',
            'zipp', 'typing-extensions', 'colorama'
        }

    def get_all_packages(self) -> List[Dict[str, Any]]:
        """Get all installed packages in the current environment."""
        packages = []

        # Try using pip list first
        pip_packages = get_pip_list()
        if pip_packages:
            for pkg in pip_packages:
                packages.append({
                    'name': pkg['name'],
                    'version': pkg['version'],
                    'source': 'pip',
                    'editable': pkg.get('editable', False)
                })
        else:
            # Fallback to importlib.metadata
            try:
                for dist in distributions():
                    packages.append({
                        'name': dist.metadata['Name'],
                        'version': dist.version,
                        'source': 'pip',
                        'editable': False
                    })
            except Exception:
                pass

        return packages

    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build a graph of package dependencies."""
        if self._dependency_graph:
            return self._dependency_graph

        dependency_graph = {}

        try:
            for dist in distributions():
                name = normalize_package_name(dist.metadata['Name'])
                dependencies = set()

                # Get requires from metadata
                if dist.requires:
                    for req_str in dist.requires:
                        try:
                            # Simple parsing - extract package name
                            dep_name = req_str.split()[0].split('>=')[0].split('==')[0].split('<')[0]
                            dep_name = normalize_package_name(dep_name)
                            dependencies.add(dep_name)
                        except Exception:
                            continue

                dependency_graph[name] = dependencies

        except Exception as e:
            print(f"Warning: Could not build complete dependency graph: {e}")

        self._dependency_graph = dependency_graph
        return dependency_graph

    def get_package_dependents(self, package_name: str) -> Set[str]:
        """Get packages that depend on the given package."""
        package_name = normalize_package_name(package_name)
        dependents = set()

        dependency_graph = self.build_dependency_graph()

        for pkg, deps in dependency_graph.items():
            if package_name in deps:
                dependents.add(pkg)

        return dependents

    def is_primary_package(self, package_name: str) -> bool:
        """
        Determine if a package is a primary (user-installed) package
        or an auto-installed dependency.
        """
        package_name = normalize_package_name(package_name)

        # Skip common utility packages
        if package_name in self.common_dependencies:
            return False

        # Check if it's a dependency of other packages
        dependents = self.get_package_dependents(package_name)

        # If no other packages depend on it, it's likely primary
        if not dependents:
            return True

        # If only one package depends on it, might be primary
        if len(dependents) == 1:
            dependent = list(dependents)[0]
            if dependent not in self.common_dependencies:
                return True

        # Default: if it has many dependents, it's probably a dependency
        return len(dependents) <= 2

    def detect_primary_packages(self) -> List[Dict[str, Any]]:
        """Detect and return only the primary (user-installed) packages."""
        all_packages = self.get_all_packages()
        primary_packages = []

        for pkg in all_packages:
            if self.is_primary_package(pkg['name']):
                # Add additional metadata
                pkg['is_primary'] = True
                pkg['dependents'] = list(self.get_package_dependents(pkg['name']))
                primary_packages.append(pkg)

        return primary_packages
