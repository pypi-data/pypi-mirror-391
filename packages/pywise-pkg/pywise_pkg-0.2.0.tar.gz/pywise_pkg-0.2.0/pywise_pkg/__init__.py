"""
pywise_pkg - Intelligent Python Dependency Management

A powerful tool for managing Python dependencies intelligently with 
conda-pip hybrid support, environment migration, and Docker optimization.
"""

__version__ = "0.1.0"
__author__ = "pywise_pkg Contributors"
__email__ = "contributors@pywise_pkg.io"

from .core.detector import DependencyDetector
from .core.resolver import HybridDependencyResolver as DependencyResolver
from .core.migrator import AdvancedEnvironmentMigrator as EnvironmentMigrator
from .core.docker_gen import DockerGenerator

__all__ = [
    "DependencyDetector",
    "DependencyResolver", 
    "EnvironmentMigrator",
    "DockerGenerator",
    "__version__",
]
