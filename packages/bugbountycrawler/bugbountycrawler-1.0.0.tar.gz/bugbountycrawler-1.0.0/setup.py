"""
Setup script for BugBountyCrawler
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bugbountycrawler",
    version="1.0.0",
    author="BugBountyCrawler Team",
    author_email="team@bugbountycrawler.dev",
    description="Production-ready bug bounty hunting platform with 30+ security scanners",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bugbountycrawler",
    packages=find_packages(exclude=["tests*", "examples*", "data*", "plugins*", "reports*", "logs*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    python_requires=">=3.11",
    install_requires=[
        "aiohttp>=3.8.0",
        "asyncio-contextmanager>=1.0.0",
        "pydantic>=1.10.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.21.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "bugbounty=bugbountycrawler.cli:app",
        ],
    },
)
