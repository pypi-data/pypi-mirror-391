"""
Advanced environment migration and format conversion
"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

class AdvancedEnvironmentMigrator:
    """
    Advanced environment migration with direct venv->conda conversion.
    """

    def __init__(self):
        self.supported_formats = ['pip', 'conda', 'poetry', 'pipenv']
        self.conda_available = self._check_conda()

    def _check_conda(self) -> bool:
        """Check if conda is available."""
        try:
            subprocess.run(['conda', '--version'], capture_output=True, check=True)
            return True
        except:
            return False

    def convert_venv_to_conda(self, 
                             env_name: Optional[str] = None,
                             python_version: Optional[str] = None,
                             keep_venv: bool = False) -> Dict[str, Any]:
        """
        Convert current venv to conda environment - SINGLE COMMAND!
        """
        try:
            if not self.conda_available:
                return {
                    'success': False,
                    'error': 'Conda not available. Please install conda/miniconda first.'
                }

            # Step 1: Detect current environment
            current_env = self._detect_current_environment()
            if current_env['type'] not in ['venv', 'system']:
                return {
                    'success': False,
                    'error': f'Current environment is {current_env["type"]}, conversion only works from venv'
                }

            # Step 2: Get installed packages
            from ..utils.helpers import get_pip_list
            packages = get_pip_list()

            # Step 3: Create conda environment name
            if env_name is None:
                env_name = Path.cwd().name.replace(' ', '-').replace('_', '-').lower()

            # Step 4: Generate environment.yml with hybrid approach
            conda_deps = []
            pip_deps = []

            # Packages that work better with conda
            conda_preferred = {
                'numpy', 'scipy', 'pandas', 'matplotlib', 'scikit-learn',
                'tensorflow', 'pytorch', 'jupyterlab', 'jupyter'
            }

            for pkg in packages:
                pkg_name = pkg['name'].lower()
                if pkg_name in conda_preferred:
                    conda_deps.append(pkg['name'])
                else:
                    pip_deps.append(f"{pkg['name']}=={pkg['version']}")

            # Create environment config
            env_config = {
                'name': env_name,
                'channels': ['conda-forge', 'defaults'],
                'dependencies': conda_deps.copy()
            }

            if python_version:
                env_config['dependencies'].insert(0, f'python={python_version}')
            else:
                env_config['dependencies'].insert(0, 'python>=3.8')

            if pip_deps:
                env_config['dependencies'].append({'pip': pip_deps})

            # Write environment.yml
            env_file = Path.cwd() / 'environment.yml'
            with open(env_file, 'w') as f:
                yaml.dump(env_config, f, default_flow_style=False, sort_keys=False)

            # Step 5: Create conda environment
            create_cmd = ['conda', 'env', 'create', '-f', str(env_file)]
            result = subprocess.run(create_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'Failed to create conda environment: {result.stderr}',
                    'files_created': [str(env_file)]
                }

            # Step 6: Backup requirements.txt if it exists
            req_file = Path.cwd() / 'requirements.txt'
            backup_created = False
            if req_file.exists():
                backup_file = req_file.with_suffix('.txt.backup')
                req_file.rename(backup_file)
                backup_created = True

            return {
                'success': True,
                'old_env': current_env,
                'new_env_name': env_name,
                'conda_packages': len(conda_deps),
                'pip_packages': len(pip_deps),
                'files_created': [str(env_file)],
                'files_backed_up': [str(backup_file)] if backup_created else [],
                'activation_command': f'conda activate {env_name}',
                'next_steps': [
                    f'Run: conda activate {env_name}',
                    'Test your application in the new environment',
                    'Delete old venv if everything works' if not keep_venv else 'Old venv preserved'
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Conversion failed: {str(e)}'
            }

    def _detect_current_environment(self) -> Dict[str, Any]:
        """Detect current environment type and details."""
        import sys

        env_info = {
            'type': 'system',
            'path': sys.executable,
            'prefix': sys.prefix
        }

        # Check for conda
        if 'conda' in sys.executable.lower() or os.environ.get('CONDA_DEFAULT_ENV'):
            env_info['type'] = 'conda'
            env_info['name'] = os.environ.get('CONDA_DEFAULT_ENV', 'base')

        # Check for virtual environment
        elif hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            env_info['type'] = 'venv'
            env_info['name'] = Path(sys.prefix).name

        return env_info

    def migrate_between_formats(self, 
                               source_file: Union[str, Path],
                               target_format: str,
                               output_file: Optional[str] = None) -> Dict[str, Any]:
        """Migrate between any dependency formats - SINGLE COMMAND!"""

        source_file = Path(source_file)
        if not source_file.exists():
            return {'success': False, 'error': f'Source file not found: {source_file}'}

        try:
            # Read source file
            source_data = self._read_dependency_file(source_file)

            # Determine output file
            if output_file is None:
                output_file = self._get_default_output_filename(target_format)

            # Convert and write
            self._write_converted_file(source_data, Path(output_file), target_format)

            return {
                'success': True,
                'source_format': source_data['format'],
                'target_format': target_format,
                'source_file': str(source_file),
                'output_file': output_file,
                'packages_converted': len(source_data.get('packages', []))
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _read_dependency_file(self, file_path: Path) -> Dict[str, Any]:
        """Read dependency file and extract packages."""

        if file_path.name in ['requirements.txt', 'requirements-dev.txt']:
            packages = []
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('-'):
                        packages.append(line)

            return {'format': 'pip', 'packages': packages}

        elif file_path.name in ['environment.yml', 'environment.yaml']:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)

            packages = []
            for dep in data.get('dependencies', []):
                if isinstance(dep, str):
                    packages.append(dep)
                elif isinstance(dep, dict) and 'pip' in dep:
                    packages.extend(dep['pip'])

            return {
                'format': 'conda',
                'packages': packages,
                'name': data.get('name', 'env'),
                'channels': data.get('channels', [])
            }

        else:
            raise ValueError(f"Unsupported file: {file_path.name}")

    def _write_converted_file(self, source_data: Dict, output_path: Path, target_format: str):
        """Write converted file in target format."""

        if target_format == 'pip':
            with open(output_path, 'w') as f:
                f.write("# Generated by pywise_pkg\n\n")
                for pkg in source_data['packages']:
                    f.write(f"{pkg}\n")

        elif target_format == 'conda':
            env_config = {
                'name': source_data.get('name', 'converted-env'),
                'channels': source_data.get('channels', ['conda-forge', 'defaults']),
                'dependencies': source_data['packages']
            }

            with open(output_path, 'w') as f:
                yaml.dump(env_config, f, default_flow_style=False)

    def _get_default_output_filename(self, format_type: str) -> str:
        """Get default output filename."""
        mapping = {
            'pip': 'requirements.txt',
            'conda': 'environment.yml',
            'poetry': 'pyproject.toml'
        }
        return mapping.get(format_type, 'requirements.txt')

    def setup_multi_environment(self, 
                               environments: List[str] = None) -> Dict[str, Any]:
        """Setup multi-environment configuration (dev/staging/prod) - SINGLE COMMAND!"""

        if environments is None:
            environments = ['dev', 'staging', 'prod']

        try:
            # Get current packages
            from ..utils.helpers import get_pip_list
            packages = get_pip_list()

            # Create base configuration
            config = {
                'project': Path.cwd().name,
                'environments': {}
            }

            files_created = []

            for env in environments:
                # Create environment-specific requirements
                env_packages = packages.copy()

                # Add dev-specific packages
                if env == 'dev':
                    dev_packages = ['pytest', 'black', 'flake8', 'mypy']
                    for pkg in dev_packages:
                        env_packages.append({'name': pkg, 'version': 'latest'})

                # Write requirements file for each environment
                req_file = Path.cwd() / f'requirements-{env}.txt'
                with open(req_file, 'w') as f:
                    f.write(f"# {env.title()} environment\n\n")
                    for pkg in env_packages:
                        if isinstance(pkg, dict):
                            version = f"=={pkg['version']}" if pkg['version'] != 'latest' else ''
                            f.write(f"{pkg['name']}{version}\n")
                        else:
                            f.write(f"{pkg}\n")

                files_created.append(str(req_file))

                # Environment config
                config['environments'][env] = {
                    'requirements_file': str(req_file),
                    'python_version': '3.11',
                    'environment_variables': self._get_env_vars(env)
                }

            # Write main config file
            config_file = Path.cwd() / 'pywise_pkg-multi-env.yml'
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)

            files_created.append(str(config_file))

            return {
                'success': True,
                'config_file': str(config_file),
                'files_created': files_created,
                'environments': environments,
                'usage': f'Use: pywise_pkg env activate {environments[0]}'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_env_vars(self, env_type: str) -> Dict[str, str]:
        """Get environment-specific variables."""
        base = {'PYTHONPATH': '.', 'PYTHONUNBUFFERED': '1'}

        if env_type == 'dev':
            base.update({'DEBUG': 'True', 'LOG_LEVEL': 'DEBUG'})
        elif env_type == 'staging':
            base.update({'DEBUG': 'False', 'LOG_LEVEL': 'INFO'})
        elif env_type == 'prod':
            base.update({'DEBUG': 'False', 'LOG_LEVEL': 'ERROR'})

        return base
