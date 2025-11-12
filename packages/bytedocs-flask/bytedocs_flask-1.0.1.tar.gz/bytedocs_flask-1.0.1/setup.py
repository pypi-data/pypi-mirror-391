"""
ByteDocs Flask - Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="bytedocs-flask",
    version="1.0.0",
    description="Automatic API documentation generator for Flask - inspired by Scramble for Laravel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ByteDocs Contributors",
    author_email="",
    url="https://github.com/aibnuhibban/bytedocs-flask",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "bytedocs_flask": [
            "ui/templates/**/*",
            "ui/templates/**/*.html",
        ],
    },
    install_requires=[
        "flask>=2.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "ai": [
            "openai>=2.0.0",
            "google-generativeai>=0.8.0",
            "anthropic>=0.70.0",
        ],
        "all": [
            "openai>=2.0.0",
            "google-generativeai>=0.8.0",
            "anthropic>=0.70.0",
        ],
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
    keywords=[
        "flask",
        "documentation",
        "api",
        "swagger",
        "openapi",
        "bytedocs",
        "auto-documentation",
        "api-doc",
        "rest-api",
        "python",
    ],
    project_urls={
        "Bug Reports": "https://github.com/aibnuhibban/bytedocs-flask/issues",
        "Source": "https://github.com/aibnuhibban/bytedocs-flask",
    },
)
