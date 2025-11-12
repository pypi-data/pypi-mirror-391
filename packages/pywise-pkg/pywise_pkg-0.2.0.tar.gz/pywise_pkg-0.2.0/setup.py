#!/usr/bin/env python3
"""
pywise_pkg - Intelligent Python Dependency Management
Advanced package with conda-pip hybrid support
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pywise_pkg",
    version="0.2.0",  # Advanced version
    author="pywise_pkg Contributors",
    author_email="shreyjain026@gmail.com",
    description="Intelligent Python dependency management with conda-pip hybrid support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shreyjain26/pywise_pkg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pywise_pkg=pywise_pkg.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
