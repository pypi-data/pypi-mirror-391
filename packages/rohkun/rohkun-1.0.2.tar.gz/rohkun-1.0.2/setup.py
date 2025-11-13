"""
Setup configuration for Rohkun CLI package.

This package provides the client-side CLI tool for code analysis.
The CLI communicates with the server via HTTP API only.
All analysis happens server-side - the CLI just uploads and displays results.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Read CLI-specific requirements
cli_requirements_file = Path(__file__).parent / "cli" / "requirements.txt"
cli_requirements = []
if cli_requirements_file.exists():
    cli_requirements = [
        line.strip()
        for line in cli_requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
else:
    # Fallback to minimal requirements (API-only, no local processing)
    cli_requirements = [
        "typer>=0.9.0",
        "rich>=13.7.0",
        "requests>=2.31.0",
        "pyperclip>=1.8.2",
    ]

setup(
    name="rohkun",
    version="1.0.2",
    description="Rohkun - Code analysis tool for detecting endpoints, API calls, and connections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rohkun Team",
    author_email="support@rohkun.com",
    url="https://github.com/rohkun/rohkun",
    packages=find_packages(exclude=["tests", "tests.*", "server", "server.*", "frontend", "frontend.*"]),
    include_package_data=True,
    install_requires=cli_requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "rohkun=cli.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords="code-analysis ast endpoints api-calls codebase-analysis",
)

