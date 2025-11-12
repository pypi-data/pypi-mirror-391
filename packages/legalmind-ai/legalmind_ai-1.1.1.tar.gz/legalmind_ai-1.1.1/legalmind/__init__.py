# File: __init__.py
"""
LegalMind AI - AI-powered legal analysis with KUHP Indonesia support
"""

__version__ = "1.1.1"
__author__ = "LegalMind AI Team"

# Import main class
from .core import LegalMindSystem, LegalMindAI, KUHPAnalyzer

__all__ = ['LegalMindSystem', 'LegalMindAI', 'KUHPAnalyzer']
