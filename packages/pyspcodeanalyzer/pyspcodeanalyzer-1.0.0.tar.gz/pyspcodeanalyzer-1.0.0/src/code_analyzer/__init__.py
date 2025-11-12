"""
Enterprise Code Analyzer Package

A comprehensive code complexity analysis tool supporting 13 programming languages
with enterprise-grade features, configurable metrics, and intuitive scoring.

Features:
- Multi-language support (SAS, Oracle, SQL Server, Python, etc.)
- Enterprise-grade architecture with configurable weights and thresholds
- 0-100 intuitive scoring system
- Automated language detection
- Batch processing capabilities
- Multiple output formats (text, JSON, CSV)
- Comprehensive metrics across 10 dimensions

Author: Code Analyzer Team
Version: 2.0.0
Date: 2025-11-11
"""

__version__ = "2.0.0"
__author__ = "Code Analyzer Team"

# Import core modules for package-level access
from .core.registry import analyzer_registry
from .core.exception import (
    UnsupportedLanguageError,
    InvalidCodeError, 
    AnalysisError,
    FileProcessingError
)
from .core.metrics import classify_complexity, get_standard_metrics
from .cli import cli, main