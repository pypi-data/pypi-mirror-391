#!/usr/bin/env python3
"""
Neuron CLI SDK - Connect any device to NexusCore MESH Network
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="san-cli",  # Changed to san-cli for PyPI
    version="1.0.3",
    author="NexusCore",
    author_email="support@nexuscore.cloud",
    description="Space Agent Network CLI - Device management and OTP authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nexus-Core-Cloud/Nexus-Support-Tickets-AI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "click>=8.0.0",
        "pyyaml>=6.0.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "san=neuron_cli.cli.main:main",  # Primary command
            "neuron-cli=neuron_cli.cli.main:main",  # Backward compatibility
        ],
    },
    keywords="cli, device-management, otp, authentication, distributed-computing",
    project_urls={
        "Bug Reports": "https://github.com/Nexus-Core-Cloud/Nexus-Support-Tickets-AI/issues",
        "Source": "https://github.com/Nexus-Core-Cloud/Nexus-Support-Tickets-AI",
    },
)
