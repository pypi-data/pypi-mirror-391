"""
Zetsubou.life Python SDK Setup

Installation and distribution configuration for the Python SDK.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Zetsubou.life Python SDK"

# Read version from __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'zetsubou', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="zetsubou-sdk",
    version=get_version(),
    author="Zetsubou.life",
    author_email="support@zetsubou.life",
    description="Python SDK for the Zetsubou.life API v2",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/zetsubou-life/python-sdk",
    project_urls={
        "Bug Reports": "https://github.com/zetsubou-life/python-sdk/issues",
        "Source": "https://github.com/zetsubou-life/python-sdk",
        "Documentation": "https://docs.zetsubou.life/python-sdk",
        "API Reference": "https://docs.zetsubou.life/api",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
            "asyncio-throttle>=1.0.0",
        ],
    },
    keywords=[
        "zetsubou",
        "api",
        "sdk",
        "ai",
        "tools",
        "image-processing",
        "video-processing",
        "file-storage",
        "chat",
        "webhooks",
    ],
    entry_points={
        "console_scripts": [
            "zetsubou=zetsubou.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)