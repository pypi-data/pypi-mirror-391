"""
Setup script for PlimverAI SDK
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="plimverai-sdk",
    version="1.0.0",
    author="PlimverAI Team",
    author_email="support@plimverai.com",
    description="Official Python SDK for PlimverAI API - Chat, RAG, Memory, Grounding with OpenAI-compatible format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Elliot-Elikplim/Zenux-Api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
        "dataclasses>=0.6; python_version < '3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "mypy>=0.800",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "cli": [
            "argparse>=1.4.0",  # Usually included in Python 3.8+
        ],
    },
    entry_points={
        'console_scripts': [
            'plimverai=plimverai_cli:main',
        ],
    },
    keywords="plimverai ai api sdk chat rag memory grounding hybrid openai llm machine-learning",
    project_urls={
        "Bug Reports": "https://github.com/Elliot-Elikplim/Zenux-Api/issues",
        "Source": "https://github.com/Elliot-Elikplim/Zenux-Api",
        "Documentation": "https://github.com/Elliot-Elikplim/Zenux-Api/tree/master/docs",
    },
)