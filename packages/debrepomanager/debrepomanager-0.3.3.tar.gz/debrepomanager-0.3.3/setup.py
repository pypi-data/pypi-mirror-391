#!/usr/bin/env python3
"""
Debian Repository Manager
Setup script for installation
"""

from setuptools import setup, find_packages
import os

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Debian Repository Manager for multi-distribution package management"

# Read requirements
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
requirements = []
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="debrepomanager",
    version="0.3.3",
    description="Debian Repository Manager for multi-distribution package management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Viacheslav Bocharov",
    author_email="vb@jethome.com",
    url="https://github.com/jethome/repomanager",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "PyYAML>=6.0",
        "click>=8.0.0",
        "python-debian>=0.1.49",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "types-PyYAML>=6.0.0",
            "types-python-dateutil>=2.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "debrepomanager=debrepomanager.cli:main",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Systems Administration",
    ],
    keywords="debian repository apt aptly package-management",
    project_urls={
        "Bug Reports": "https://github.com/jethome/repomanager/issues",
        "Source": "https://github.com/jethome/repomanager",
    },
)



