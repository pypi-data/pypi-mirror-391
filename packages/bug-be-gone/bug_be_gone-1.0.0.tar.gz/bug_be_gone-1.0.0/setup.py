#!/usr/bin/env python3
"""
Setup configuration for Bug-Be-Gone PyPI package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
long_description = Path("README_PYPI.md").read_text(encoding="utf-8")

setup(
    name="bug-be-gone",
    version="1.0.0",
    author="Keeg",
    author_email="keeg@dishesandmore.com",
    description="Automatically detect and fix Python errors - never debug again",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bug-be-gone",  # Update with actual repo
    packages=find_packages(),
    py_modules=["bug_be_gone"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # No external dependencies - pure Python
    ],
    entry_points={
        "console_scripts": [
            "bug-be-gone=bug_be_gone:main",
            "bbg=bug_be_gone:main",  # Short alias
        ],
    },
    keywords="debugger, error-fixing, automatic-debugging, python-errors, development-tools",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/bug-be-gone/issues",
        "Source": "https://github.com/yourusername/bug-be-gone",
        "Documentation": "https://github.com/yourusername/bug-be-gone#readme",
    },
    license="Proprietary - Trial License",
    include_package_data=True,
)
