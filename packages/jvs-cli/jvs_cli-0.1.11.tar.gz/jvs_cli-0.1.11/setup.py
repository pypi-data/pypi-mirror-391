from setuptools import setup, find_packages
from pathlib import Path
import re

def get_version():
    init_path = Path(__file__).parent / "jarvis_cli" / "__init__.py"
    content = init_path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string")

requirements_path = Path(__file__).parent / "requirements.txt"
requirements = requirements_path.read_text().splitlines() if requirements_path.exists() else []

readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="jvs-cli",
    version=get_version(),
    description="Terminal-based AI chat interface with streaming support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JVS CLI Contributors",
    license="Apache-2.0",
    packages=find_packages(exclude=["tests*", "jarvis_cli_golang*"]),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jvs-cli=jarvis_cli.cli:app",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
