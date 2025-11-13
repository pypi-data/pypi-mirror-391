"""
Setup script for L'Agent - Minimal Local LLM Agent Framework
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lagents",
    version="0.1.1",
    author="BenevolentJoker",
    author_email="benevolentjoker@example.com",
    description="L'Agent - Minimal experimental framework for building agents with local LLM deployments. Zero bloat, maximum simplicity.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BenevolentJoker-JohnL/agents",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="llm agents ollama local minimal framework llama vllm lagent",
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "distributed": [
            "sollol>=0.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.950",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/BenevolentJoker-JohnL/agents/issues",
        "Source": "https://github.com/BenevolentJoker-JohnL/agents",
        "Documentation": "https://github.com/BenevolentJoker-JohnL/agents#readme",
    },
)
