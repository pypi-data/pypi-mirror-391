"""
Setup script for trading-data-client.

For backward compatibility with older pip versions.
Modern installations should use pyproject.toml.
"""

from setuptools import setup

# Read version from package
with open("trading_data_client/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="trading-data-client",
    version=version,
    description="Python client library for Trading Data Server - fetch historical and real-time market data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Benjamin Cham",
    author_email="benjamincham@users.noreply.github.com",
    url="https://github.com/benjamincham/moonbase_Datahub",
    project_urls={
        "Bug Tracker": "https://github.com/benjamincham/moonbase_Datahub/issues",
        "Documentation": "https://github.com/benjamincham/moonbase_Datahub#readme",
        "Source Code": "https://github.com/benjamincham/moonbase_Datahub",
    },
    packages=["trading_data_client"],
    package_data={
        "trading_data_client": ["py.typed", "README.md"],
    },
    install_requires=[
        "requests>=2.28.0",
        "pyzmq>=25.0.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "responses>=0.22.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
        ]
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    keywords="trading market-data ohlcv real-time streaming alpaca yfinance historical-data",
)
