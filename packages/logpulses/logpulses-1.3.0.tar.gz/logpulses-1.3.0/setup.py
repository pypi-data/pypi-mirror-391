from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="logpulses",
    version="1.3.0",
    description="Comprehensive request/response logging middleware for FastAPI with storage options and zero configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hariharan S",
    author_email="hvasan59@gmail.com",
    url="https://github.com/Hari-vasan/logpulses",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.100.0",
        "starlette>=0.27.0",
        "psutil>=5.9.0",
        "schedule>=1.2.0",  # Required for automatic log cleanup
    ],
    extras_require={
        # Database storage options
        "mongodb": [
            "pymongo>=4.5.0",
        ],
        "mysql": [
            "mysql-connector-python>=8.2.0",
        ],
        "postgresql": [
            "psycopg2-binary>=2.9.0",
        ],
        # All database support
        "all-db": [
            "pymongo>=4.5.0",
            "mysql-connector-python>=8.2.0",
            "psycopg2-binary>=2.9.0",
        ],
        # Development dependencies
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        # Complete installation (all features)
        "full": [
            "pymongo>=4.5.0",
            "mysql-connector-python>=8.2.0",
            "psycopg2-binary>=2.9.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    keywords=[
        "fastapi",
        "logging",
        "middleware",
        "request-logging",
        "api-logging",
        "monitoring",
        "observability",
        "database-logging",
        "log-storage",
        "mongodb",
        "mysql",
        "postgresql",
        "sqlite",
        "automatic-cleanup",
        "production-logging",
    ],
    project_urls={
        "Homepage": "https://github.com/Hari-vasan/logpulses",
        "Documentation": "https://github.com/Hari-vasan/logpulses#readme",
        "Repository": "https://github.com/Hari-vasan/logpulses",
        "Bug Tracker": "https://github.com/Hari-vasan/logpulses/issues",
        "Changelog": "https://github.com/Hari-vasan/logpulses/blob/main/CHANGELOG.md",
    },
    zip_safe=False,
)
