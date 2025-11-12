"""
Advanced Docker integration and Dockerfile generation module
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

class DockerGenerator:
    """Generate optimized Docker configurations with intelligent analysis."""

    def __init__(self):
        self.base_images = {
            '3.8': 'python:3.8-slim',
            '3.9': 'python:3.9-slim', 
            '3.10': 'python:3.10-slim',
            '3.11': 'python:3.11-slim',
            '3.12': 'python:3.12-slim',
            'default': 'python:3.11-slim'
        }

        # System dependencies for packages
        self.package_deps = {
            'pillow': ['libjpeg-dev', 'zlib1g-dev'],
            'psycopg2': ['libpq-dev', 'gcc'],
            'numpy': ['gcc', 'g++', 'libblas-dev'],
            'pandas': ['gcc', 'g++'],
            'opencv-python': ['libglib2.0-0', 'libsm6'],
            'tensorflow': ['gcc', 'g++'],
            'torch': ['gcc', 'g++']
        }

        # Web frameworks
        self.web_frameworks = {
            'django': {'port': 8000, 'cmd': ['python', 'manage.py', 'runserver', '0.0.0.0:8000']},
            'flask': {'port': 5000, 'cmd': ['python', 'app.py']}, 
            'fastapi': {'port': 8000, 'cmd': ['uvicorn', 'main:app', '--host', '0.0.0.0']},
            'streamlit': {'port': 8501, 'cmd': ['streamlit', 'run', 'app.py']}
        }

    def analyze_project(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project to determine optimal Docker configuration."""
        packages = []
        try:
            # Import here to avoid circular imports
            from ..utils.helpers import get_pip_list
            pip_packages = get_pip_list()
            packages = [{'name': pkg['name'], 'version': pkg['version']} for pkg in pip_packages]
        except:
            pass

        package_names = {pkg['name'].lower() for pkg in packages}

        # Detect project type
        web_framework = None
        for framework in self.web_frameworks:
            if framework in package_names:
                web_framework = framework
                break

        # Detect ML project
        ml_packages = {'tensorflow', 'torch', 'scikit-learn', 'pandas', 'numpy'}
        is_ml = bool(package_names & ml_packages)

        # System dependencies
        system_deps = set()
        for pkg in packages:
            pkg_name = pkg['name'].lower()
            if pkg_name in self.package_deps:
                system_deps.update(self.package_deps[pkg_name])

        return {
            'packages': packages,
            'web_framework': web_framework,
            'is_ml': is_ml,
            'system_deps': sorted(system_deps),
            'has_requirements': (project_path / 'requirements.txt').exists(),
            'estimated_size_mb': 150 + len(packages) * 5
        }

    def generate_dockerfile(self, project_path: Path, python_version: str = '3.11') -> str:
        """Generate optimized Dockerfile."""
        analysis = self.analyze_project(project_path)
        base_image = self.base_images.get(python_version, self.base_images['default'])

        lines = [
            f"FROM {base_image}",
            "",
            "# Set working directory", 
            "WORKDIR /app"
        ]

        # System dependencies
        if analysis['system_deps']:
            lines.extend([
                "",
                "# Install system dependencies",
                "RUN apt-get update && apt-get install -y --no-install-recommends \\",
                f"    {' '.join(analysis['system_deps'])} \\",
                "    && rm -rf /var/lib/apt/lists/*"
            ])

        # Python dependencies
        if analysis['has_requirements']:
            lines.extend([
                "",
                "# Copy and install Python dependencies",
                "COPY requirements.txt .",
                "RUN pip install --no-cache-dir -r requirements.txt"
            ])

        # Copy application
        lines.extend([
            "",
            "# Copy application code",
            "COPY . .",
            "",
            "# Create non-root user",
            "RUN groupadd -r appuser && useradd -r -g appuser appuser",
            "RUN chown -R appuser:appuser /app",
            "USER appuser"
        ])

        # Expose port and set command
        if analysis['web_framework']:
            framework_config = self.web_frameworks[analysis['web_framework']]
            lines.extend([
                "",
                f"EXPOSE {framework_config['port']}",
                f"CMD {framework_config['cmd']}"
            ])
        else:
            lines.extend([
                "",
                'CMD ["python", "main.py"]'
            ])

        return "\n".join(lines)

    def dockerize_project(self, project_path: Optional[Path] = None, **kwargs) -> Dict[str, Any]:
        """Complete dockerization in one command."""
        if project_path is None:
            project_path = Path.cwd()

        try:
            # Generate files
            dockerfile = self.generate_dockerfile(project_path, kwargs.get('python_version', '3.11'))

            # Write Dockerfile
            with open(project_path / 'Dockerfile', 'w') as f:
                f.write(dockerfile)

            # Write .dockerignore
            dockerignore = """__pycache__/
*.pyc
.git/
.vscode/
tests/
docs/
"""
            with open(project_path / '.dockerignore', 'w') as f:
                f.write(dockerignore)

            analysis = self.analyze_project(project_path)

            return {
                'success': True,
                'files_created': ['Dockerfile', '.dockerignore'],
                'analysis': analysis
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}
