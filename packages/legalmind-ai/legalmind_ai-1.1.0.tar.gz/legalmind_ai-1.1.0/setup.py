from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get package version from __init__.py if available
def get_version():
    try:
        with open("legalmind/__init__.py", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"\'')
    except FileNotFoundError:
        pass
    return "1.1.0"

# Find all package data files recursively
def find_package_data(package, data_dirs):
    """
    Find all data files in specified directories recursively
    """
    package_data = []
    for data_dir in data_dirs:
        data_dir_path = Path(package) / data_dir
        if data_dir_path.exists():
            # Add all files in directory and subdirectories
            for file_path in data_dir_path.rglob('*'):
                if file_path.is_file():
                    # Convert to package data format
                    rel_path = file_path.relative_to(package)
                    package_data.append(str(rel_path))
    return package_data

setup(
    name="legalmind-ai",
    version=get_version(),
    author="LegalMind AI",
    author_email="contact@legalmind.ai",
    description="AI-Powered Legal Assistant for Indonesian Law with KUHP Baru 2026 Support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/creatoross/legalmind-ai",
    
    # Package discovery
    packages=find_packages(include=['legalmind', 'legalmind.*']),
    
    # Classifiers for PyPI
    classifiers=[
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Legal Industry",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Linguistic",
    "Topic :: Office/Business",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
],
    
    # Python requirements
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "requests>=2.25.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
    ],
    
    # Optional dependencies for enhanced features
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
            "pre-commit>=2.15",
        ],
        "web": [
            "jinja2>=3.0",
            "aiofiles>=0.7",
            "python-multipart>=0.0.5",
        ],
        "ml": [
            "transformers>=4.0",
            "torch>=1.9",
            "sentence-transformers>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ]
    },
    
    # Entry points for command line interface
    entry_points={
        'console_scripts': [
            'legalmind=legalmind.cli:main',
            'legalmind-analyze=legalmind.analyzers.cli:analyze_cli',
            'legalmind-kuhp=legalmind.kuhp_baru_2026.cli:kuhp_cli [kuhp]',
        ],
    },
    
    # Include package data
    include_package_data=True,
    
    # Package data specification
    package_data={
        'legalmind': [
            # Study cases and legal documents
            'study_cases/*',
            'study_cases/*.md',
            'study_cases/*.py',
            
            # KUHP Baru 2026 specific files
            'study_cases/kuhp_baru_2026/*',
            'study_cases/kuhp_baru_2026/**/*',
            'study_cases/kuhp_baru_2026/**/**/*',
            
            # Configuration files
            'config/*.json',
            'config/*.yaml',
            'config/*.yml',
            
            # Prompt templates
            'prompt_templates/*.txt',
            'prompt_templates/*.json',
            
            # AI model configurations
            'ai/models/*.json',
            'ai/models/*.yaml',
            
            # API specifications
            'api/*.json',
            'api/*.yaml',
        ],
    },
    
    # Metadata for search optimization
    keywords=[
        "legal", "ai", "artificial-intelligence", "indonesian-law",
        "hukum", "indonesia", "legal-tech", "law-ai",
        "kuhp-baru", "kuhp-2026", "legal-analysis",
        "contract-review", "legal-research", "nlp"
    ],
    
    # Project URLs
    project_urls={
        "Homepage": "https://github.com/creatoross/legalmind-ai",
        "Documentation": "https://legalmind-ai.readthedocs.io",
        "Source": "https://github.com/creatoross/legalmind-ai",
        "Tracker": "https://github.com/creatoross/legalmind-ai/issues",
        "Changelog": "https://github.com/creatoross/legalmind-ai/releases",
    },
    
    # License
    license="MIT",
    
    # Additional metadata
    platforms=["any"],
    zip_safe=False,
    
    # Security contact
    provide=["legalmind"],
    
    # Obsoletes old packages if any
    obsoletes=[],
)
