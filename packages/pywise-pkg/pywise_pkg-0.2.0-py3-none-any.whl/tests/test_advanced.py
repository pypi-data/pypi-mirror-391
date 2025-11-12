"""
Tests for pywise_pkg Advanced Features
"""

import pytest
from pywise_pkg import DependencyDetector, DependencyResolver, EnvironmentMigrator, DockerGenerator

def test_dependency_detector():
    """Test primary package detection."""
    detector = DependencyDetector()
    packages = detector.get_all_packages()
    primary = detector.detect_primary_packages()

    assert isinstance(packages, list)
    assert isinstance(primary, list)
    assert len(primary) <= len(packages)

def test_hybrid_resolver():
    """Test conda-pip hybrid resolution."""
    resolver = DependencyResolver()
    packages = ['numpy', 'flask']
    analysis = resolver.analyze_package_sources(packages)

    assert 'conda_packages' in analysis
    assert 'pip_packages' in analysis
    assert 'recommendations' in analysis

def test_environment_migrator():
    """Test environment detection."""
    migrator = EnvironmentMigrator()
    env_info = migrator._detect_current_environment()

    assert 'type' in env_info
    assert env_info['type'] in ['conda', 'venv', 'pipenv', 'poetry', 'system']

def test_docker_generator():
    """Test Docker configuration generation."""
    docker_gen = DockerGenerator()
    analysis = docker_gen.analyze_project(Path('.'))

    assert 'packages' in analysis
    assert 'estimated_size_mb' in analysis
    assert 'system_deps' in analysis

if __name__ == '__main__':
    pytest.main([__file__])
