"""Setup script for tabstack-ai package."""

from setuptools import find_packages, setup

# Read the contents of README file
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Python SDK for TABStack AI"

setup(
    name="tabstack-ai",
    version="1.0.0",
    author="TABStack",
    author_email="support@tabstack.ai",
    description="Python SDK for TABStack AI - Extract, Generate, and Automate web content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tabstack/tabs-python",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.27.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
    },
    package_data={
        "tabstack_ai": ["py.typed"],
    },
    keywords="web-scraping ai automation data-extraction web-automation",
    project_urls={
        "Documentation": "https://docs.tabstack.ai",
        "Bug Tracker": "https://github.com/tabstack/tabs-python/issues",
        "Source Code": "https://github.com/tabstack/tabs-python",
    },
)
