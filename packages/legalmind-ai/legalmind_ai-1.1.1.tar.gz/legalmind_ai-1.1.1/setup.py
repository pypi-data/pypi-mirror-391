# File: setup.py
from setuptools import setup, find_packages

setup(
    name="legalmind-ai-indonesia",  # Nama yang lebih unik
    version="1.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0", 
        "pydantic>=1.8.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered legal analysis with KUHP Indonesia support - Deepfake, Corruption, Environmental Crime Detection",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="legal ai kuhp indonesia compliance analysis deepfake corruption environmental crime",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries",
    ],
)
