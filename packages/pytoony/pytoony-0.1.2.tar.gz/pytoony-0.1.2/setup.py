"""
Setup configuration for pytoony package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name="pytoony",
    version="0.1.2",
    description="Convert between TOON (Token Oriented Object Notation) and JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="puchkoff",
    url="https://github.com/puchkoff/pytoony",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    tests_require=[
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pytoony=pytoony.cli:main",
        ],
    },
)

