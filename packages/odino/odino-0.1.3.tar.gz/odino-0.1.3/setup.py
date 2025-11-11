"""
Setup script for Odino CLI
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="odino",
    version="0.1.3",
    author="Carlo Esposito",
    author_email="carlo@aploi.de",
    license="GPL-3.0-only",
    description="Local semantic search CLI for code and text files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cesp99/odino",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.11",
    install_requires=[
        "typer>=0.9.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "rich>=13.0.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "odino=odino.cli:app",
        ],
    },
)
