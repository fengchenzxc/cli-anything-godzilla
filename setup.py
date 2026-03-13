"""
PyPI package configuration for cli-anything-godzilla.

This package provides a CLI harness for the Godzilla Security Testing Tool.
"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-godzilla",
    version="1.0.0",
    packages=find_namespace_packages(include=["cli_anything.godzilla"]),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-godzilla=cli_anything.godzilla.godzilla_cli:main",
        ],
    },
    python_requires=">=3.10",
)
