"""
SERAA Setup Configuration
Stochastic Emergent Reasoning Alignment Architecture - Ethical AI Framework
"""

from setuptools import setup, find_packages
from pathlib import Path


# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""


setup(
    name="seraa",
    version="0.2.3",  # Incremented for new benchmark features
    author="Theodore Park",
    author_email="theodore.jb.park@gmail.com",  # Fixed double .com
    description="Stochastic Emergent Reasoning Alignment Architecture - Ethical AI Framework with PAC evaluation and regulatory benchmarks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tpark216/seraa",
    project_urls={
        "Bug Tracker": "https://github.com/tpark216/seraa/issues",
        "Documentation": "https://github.com/tpark216/seraa#readme",
        "Source Code": "https://github.com/tpark216/seraa",
        "Benchmarks": "https://github.com/tpark216/seraa/tree/main/tests/benchmarks",
    },
    
    # Find all packages, exclude test/example directories from installation
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    
    # Include package data (configs, etc.)
    include_package_data=True,
    
    # Specify non-Python files to include in the package
    package_data={
        'seraa': [
            'config/*.json',
            'config/*.yaml',
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    
    python_requires=">=3.8",
    
    install_requires=[
        "requests>=2.31.0",  # For LLM integration (Ollama)
        "numpy>=1.21.0",     # Core dependency for PAC calculations
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-xdist>=3.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
        "llm-full": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
        ],
        "viz": [
            "matplotlib>=3.5.0",
            "seaborn>=0.12.0",  
        ],
        "benchmarks": [
            "matplotlib>=3.5.0",
            "seaborn>=0.12.0",
        ],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.12.0",
            "pytest>=7.0.0",
        ]
    },
    
    entry_points={
        "console_scripts": [
            "seraa-chat=seraa.cli.chat:main",
            "seraa-eval=seraa.cli.evaluate:main",
        ],
    },
    
    keywords=[
        "ai-ethics",
        "responsible-ai",
        "ethical-ai",
        "agency-preservation",
        "digital-ethics",
        "moral-reasoning",
        "ai-alignment",
        "llm",
        "ethics-framework",
        "pac",
        "agentic-capacity",
        "regulatory-compliance",
        "gdpr",
        "hipaa",
        "ai-act",
        "benchmark",
        "explainable-ai",
    ],
    
    zip_safe=False,
)
