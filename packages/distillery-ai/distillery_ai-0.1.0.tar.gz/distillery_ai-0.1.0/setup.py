"""
Distillery setup configuration.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="distillery-ai",
    version="0.1.0",
    author="Distillery",
    author_email="hello@distillery.ai",
    description="Convert RAG logs into fine-tuning datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/distillery",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "openai>=1.0.0",
    ],
    extras_require={
        "langsmith": ["langsmith>=0.1.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "distillery=cli.main:main",
        ],
    },
)
