"""
Utility functions and helpers for pywise_pkg
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

def get_python_executable() -> str:
    """Get the current Python executable path."""
    return sys.executable

def run_command(cmd: List[str], capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        if not check:
            return e
        raise

def is_conda_environment() -> bool:
    """Check if we're running in a conda environment."""
    return (
        os.environ.get('CONDA_DEFAULT_ENV') is not None or
        os.environ.get('CONDA_PREFIX') is not None or
        'conda' in sys.executable.lower() or
        'anaconda' in sys.executable.lower()
    )

def is_virtual_environment() -> bool:
    """Check if we're running in a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

def get_environment_type() -> str:
    """Detect the type of Python environment."""
    if is_conda_environment():
        return 'conda'
    elif is_virtual_environment():
        return 'venv'
    elif 'pipenv' in sys.executable:
        return 'pipenv'
    elif Path('poetry.lock').exists() or Path('pyproject.toml').exists():
        return 'poetry'
    else:
        return 'system'

def normalize_package_name(name: str) -> str:
    """Normalize package name according to PEP 508."""
    import re
    return re.sub(r'[-_.]+', '-', name).lower()

def get_pip_list() -> List[Dict]:
    """Get list of installed packages from pip."""
    try:
        result = run_command([get_python_executable(), '-m', 'pip', 'list', '--format=json'])
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []

def find_project_root() -> Optional[Path]:
    """Find the project root directory by looking for common files."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        # Look for common project indicators
        if any(
            (parent / filename).exists()
            for filename in [
                'setup.py', 'setup.cfg', 'pyproject.toml', 'requirements.txt',
                'Pipfile', 'poetry.lock', 'environment.yml', '.git', '.pywise_pkg.yml'
            ]
        ):
            return parent
    return current
