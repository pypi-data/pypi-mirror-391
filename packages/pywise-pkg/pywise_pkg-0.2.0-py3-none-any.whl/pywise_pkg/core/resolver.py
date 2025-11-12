"""
Advanced dependency resolution with conda-pip hybrid support
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union

class HybridDependencyResolver:
    """
    Conda-pip hybrid resolver that bridges both ecosystems.
    """

    def __init__(self):
        self.conda_available = self._check_conda_availability()
        self.pip_to_conda_mapping = {
            # Common pip -> conda name mappings
            'opencv-python': 'opencv',
            'pillow': 'pillow',
            'scikit-learn': 'scikit-learn', 
            'tensorflow': 'tensorflow',
            'pytorch': 'pytorch',
            'beautifulsoup4': 'beautifulsoup4',
            'pyyaml': 'pyyaml',
            'msgpack': 'msgpack-python',
            'pyqt5': 'pyqt',
        }

        # Packages better installed via conda
        self.prefer_conda = {
            'numpy', 'scipy', 'pandas', 'matplotlib', 'scikit-learn',
            'tensorflow', 'pytorch', 'opencv', 'pillow', 'numba',
            'jupyterlab', 'jupyter', 'ipython', 'spyder'
        }

        # Packages that should stay with pip
        self.prefer_pip = {
            'flask', 'django', 'fastapi', 'requests', 'click', 'rich',
            'pydantic', 'sqlalchemy', 'alembic', 'celery'
        }

    def _check_conda_availability(self) -> bool:
        """Check if conda is available."""
        try:
            subprocess.run(['conda', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def analyze_package_sources(self, packages: List[str]) -> Dict[str, Any]:
        """Analyze which packages should come from conda vs pip."""
        analysis = {
            'conda_packages': [],
            'pip_packages': [],
            'conflicts': [],
            'recommendations': []
        }

        for pkg in packages:
            pkg_name = pkg.split('>=')[0].split('==')[0].split('<')[0]
            pkg_lower = pkg_name.lower()

            if pkg_lower in self.prefer_conda:
                conda_name = self.pip_to_conda_mapping.get(pkg_lower, pkg_name)
                analysis['conda_packages'].append({
                    'original': pkg,
                    'conda_name': conda_name,
                    'reason': 'Better performance/compatibility'
                })
            elif pkg_lower in self.prefer_pip:
                analysis['pip_packages'].append({
                    'original': pkg,
                    'reason': 'Pip ecosystem package'
                })
            else:
                # Default to pip, but check conda availability
                analysis['pip_packages'].append({
                    'original': pkg,
                    'reason': 'Default to pip'
                })

        # Generate recommendations
        if analysis['conda_packages'] and not self.conda_available:
            analysis['recommendations'].append(
                "Install conda/miniconda for better scientific package management"
            )

        if len(analysis['conda_packages']) > len(analysis['pip_packages']) * 2:
            analysis['recommendations'].append(
                "Consider using conda as primary package manager for this project"
            )

        return analysis

    def resolve_hybrid_environment(self, 
                                 packages: List[str],
                                 target_format: str = 'conda') -> Dict[str, Any]:
        """Resolve packages using optimal conda-pip hybrid approach."""

        analysis = self.analyze_package_sources(packages)

        if target_format == 'conda' and self.conda_available:
            return self._create_conda_hybrid_solution(analysis)
        else:
            return self._create_pip_solution(analysis)

    def _create_conda_hybrid_solution(self, analysis: Dict) -> Dict[str, Any]:
        """Create conda environment with pip dependencies."""
        conda_deps = []
        pip_deps = []

        # Process conda packages
        for pkg_info in analysis['conda_packages']:
            conda_deps.append(pkg_info['conda_name'])

        # Process pip packages
        for pkg_info in analysis['pip_packages']:
            pip_deps.append(pkg_info['original'])

        # Create conda environment config
        env_config = {
            'name': 'hybrid-env',
            'channels': ['conda-forge', 'defaults'],
            'dependencies': conda_deps
        }

        if pip_deps:
            env_config['dependencies'].append({'pip': pip_deps})

        return {
            'success': True,
            'format': 'conda_hybrid',
            'config': env_config,
            'conda_packages': len(conda_deps),
            'pip_packages': len(pip_deps),
            'recommendations': analysis['recommendations']
        }

    def _create_pip_solution(self, analysis: Dict) -> Dict[str, Any]:
        """Create pip-only solution."""
        all_packages = []

        for pkg_info in analysis['conda_packages']:
            all_packages.append(pkg_info['original'])

        for pkg_info in analysis['pip_packages']:
            all_packages.append(pkg_info['original'])

        return {
            'success': True, 
            'format': 'pip',
            'packages': all_packages,
            'recommendations': analysis['recommendations'] + [
                "Some packages might perform better with conda installation"
            ]
        }

    def convert_requirements_to_conda(self, requirements_file: Path) -> Dict[str, Any]:
        """Convert requirements.txt to conda environment.yml with hybrid approach."""
        try:
            with open(requirements_file, 'r') as f:
                lines = f.readlines()

            packages = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    packages.append(line)

            result = self.resolve_hybrid_environment(packages, 'conda')

            if result['success']:
                # Write environment.yml
                env_file = requirements_file.parent / 'environment.yml'
                with open(env_file, 'w') as f:
                    import yaml
                    yaml.dump(result['config'], f, default_flow_style=False)

                result['output_file'] = str(env_file)

            return result

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def find_compatible_versions(self, packages: List[str]) -> Dict[str, str]:
        """Find compatible versions across conda and pip."""
        # This is a simplified version - in production you'd query both conda and PyPI APIs
        resolved = {}

        for pkg in packages:
            pkg_name = pkg.split('>=')[0].split('==')[0].split('<')[0]
            # For now, just return the package as-is
            # In a full implementation, this would resolve version conflicts
            resolved[pkg_name] = 'latest'

        return resolved
