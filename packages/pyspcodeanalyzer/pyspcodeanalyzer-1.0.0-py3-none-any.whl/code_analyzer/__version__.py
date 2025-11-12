"""
Version information for Code Analyzer package.

This module provides version information for the code analyzer package.
The version follows Semantic Versioning (https://semver.org/).
"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Release information
__author__ = "Code Analyzer Team"
__email__ = "support@codeanalyzer.dev"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 Code Analyzer Team"

# Package metadata
__title__ = "code-analyzer"
__description__ = "Enterprise-grade code complexity analyzer supporting 14 programming languages"
__url__ = "https://github.com/codeanalyzer/code-analyzer"

# Build information
__build_date__ = "2025-11-11"
__python_requires__ = ">=3.8"

# Feature flags for this version
FEATURES = {
    "multi_language_support": True,
    "cli_interface": True,
    "config_management": True,
    "enterprise_metrics": True,
    "intelligent_detection": True,
    "extensible_architecture": True,
}

# Supported languages in this version
SUPPORTED_LANGUAGES = [
    "bigquery",
    "db2", 
    "mysql",
    "oracle",
    "postgresql",
    "pyspark",
    "python",
    "redshift",
    "sas",
    "snowflake",
    "sparksql",
    "sqlite",
    "sqlserver",
    "sybase"
]

def get_version() -> str:
    """
    Get the current version string.
    
    Returns:
        str: Version string in semantic version format
    """
    return __version__

def get_version_info() -> tuple:
    """
    Get the current version as a tuple of integers.
    
    Returns:
        tuple: Version tuple (major, minor, patch)
    """
    return __version_info__

def get_full_version_info() -> dict:
    """
    Get comprehensive version and package information.
    
    Returns:
        dict: Complete version and metadata information
    """
    return {
        "version": __version__,
        "version_info": __version_info__,
        "title": __title__,
        "description": __description__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "url": __url__,
        "build_date": __build_date__,
        "python_requires": __python_requires__,
        "supported_languages": SUPPORTED_LANGUAGES,
        "features": FEATURES
    }

# Convenience imports for version checking
version = __version__
version_info = __version_info__