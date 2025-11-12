"""
Enterprise-Grade Analyzer Registry System

This module provides a dynamic analyzer registration and discovery system
that enables plugin architecture, runtime analyzer selection, and clean
separation of concerns for enterprise modularity.

Author: Code Analyzer Team
Version: 2.0.0
Date: 2025-11-11
"""

import re
from typing import Dict, List, Type, Optional, Tuple
from .analyzer_base import AnalyzerBase
from .exception import UnsupportedLanguageError, ConfigurationError


class AnalyzerRegistry:
    """
    Central registry for all code analyzers with dynamic registration
    and language detection capabilities.
    
    This registry enables:
    - Dynamic analyzer registration without hardcoding
    - Runtime analyzer selection
    - Language auto-detection
    - Plugin architecture support
    - Enterprise modularity
    """
    
    _instance = None
    _analyzers: Dict[str, Type[AnalyzerBase]] = {}
    _language_patterns: Dict[str, List[str]] = {}
    
    def __new__(cls):
        """Singleton pattern to ensure single registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize registry with default analyzers if not already initialized."""
        if not hasattr(self, '_initialized'):
            self._initialize_default_analyzers()
            self._initialize_language_patterns()
            self._initialized = True
    
    def _initialize_default_analyzers(self):
        """Initialize registry with all available analyzers."""
        try:
            # Import all analyzer modules
            from ..analyzers.sas_analyzer import SASAnalyzer
            from ..analyzers.sybase_analyzer import SybaseAnalyzer
            from ..analyzers.oracle_analyzer import OracleAnalyzer
            from ..analyzers.sqlserver_analyzer import SQLServerAnalyzer
            from ..analyzers.mysql_analyzer import MySQLAnalyzer
            from ..analyzers.postgresql_analyzer import PostgreSQLAnalyzer
            from ..analyzers.python_analyzer import PythonAnalyzer
            from ..analyzers.bigquery_analyzer import BigQueryAnalyzer
            from ..analyzers.snowsql_analyzer import SnowSQLAnalyzer
            from ..analyzers.sparksql_analyzer import SparkSQLAnalyzer
            from ..analyzers.pyspark_analyzer import PySparkAnalyzer
            from ..analyzers.db2_analyzer import DB2Analyzer
            from ..analyzers.redshift_analyzer import RedshiftAnalyzer
            from ..analyzers.sqlite_analyzer import SQLiteAnalyzer
            
            # Register all analyzers
            self.register_analyzer("sas", SASAnalyzer)
            self.register_analyzer("sybase", SybaseAnalyzer)
            self.register_analyzer("oracle", OracleAnalyzer)
            self.register_analyzer("sqlserver", SQLServerAnalyzer)
            self.register_analyzer("mysql", MySQLAnalyzer)
            self.register_analyzer("postgresql", PostgreSQLAnalyzer)
            self.register_analyzer("python", PythonAnalyzer)
            self.register_analyzer("bigquery", BigQueryAnalyzer)
            self.register_analyzer("snowflake", SnowSQLAnalyzer)
            self.register_analyzer("sparksql", SparkSQLAnalyzer)
            self.register_analyzer("pyspark", PySparkAnalyzer)
            self.register_analyzer("db2", DB2Analyzer)
            self.register_analyzer("redshift", RedshiftAnalyzer)
            self.register_analyzer("sqlite", SQLiteAnalyzer)
            
        except ImportError as e:
            raise ConfigurationError(
                f"Failed to import analyzer modules: {str(e)}",
                config_key="analyzer_imports"
            )
    
    def _initialize_language_patterns(self):
        """Initialize language detection patterns."""
        self._language_patterns = {
            # SAS patterns
            "sas": [
                r'\bdata\s+\w+\s*;',
                r'\bproc\s+\w+\b',
                r'\brun\s*;',
                r'\bquit\s*;',
                r'%macro\s+\w+',
                r'%let\s+\w+\s*='
            ],
            
            # Python patterns
            "python": [
                r'^import\s+\w+',
                r'^from\s+\w+\s+import',
                r'def\s+\w+\s*\(',
                r'class\s+\w+\s*[\(\:]',
                r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
                r'@\w+',  # decorators
                r'^\s*#.*python'  # shebang or comments
            ],
            
            # SQL patterns (generic - will need refinement for specific dialects)
            "sqlserver": [
                r'\bCREATE\s+PROCEDURE\b',
                r'\bDECLARE\s+@\w+',
                r'\bBEGIN\s+TRY\b',
                r'\bRAISERROR\b',
                r'\bGO\s*$'
            ],
            
            "oracle": [
                r'\bCREATE\s+OR\s+REPLACE\s+PACKAGE\b',
                r'\bDECLARE\s*$',
                r'\bBEGIN\s*$',
                r'\bEND\s*;',
                r'\bDBMS_OUTPUT\.PUT_LINE\b',
                r'\bEXCEPTION\s+WHEN\b'
            ],
            
            "mysql": [
                r'\bDELIMITER\s+',
                r'\bCREATE\s+DEFINER\s*=',
                r'\bENGINE\s*=\s*InnoDB\b',
                r'AUTO_INCREMENT\s*=',
                r'\bSHOW\s+TABLES\b'
            ],
            
            "postgresql": [
                r'\bCREATE\s+OR\s+REPLACE\s+FUNCTION\b',
                r'\$\$\s*$',
                r'\bLANGUAGE\s+plpgsql\b',
                r'\bRETURNS\s+\w+\s+AS\b',
                r'\bPERFORM\s+\w+'
            ],
            
            "bigquery": [
                r'\bCREATE\s+OR\s+REPLACE\s+TABLE\s+`',
                r'`\w+\.\w+\.\w+`',
                r'\bPARTITION\s+BY\s+DATE\b',
                r'\bARRAY\[',
                r'\bSTRUCT\['
            ],
            
            "snowflake": [
                r'\bCREATE\s+OR\s+REPLACE\s+STREAM\b',
                r'\bCREATE\s+OR\s+REPLACE\s+TASK\b',
                r'\bRETURNS\s+TABLE\s*\(',
                r'\bLANGUAGE\s+JAVASCRIPT\b',
                r'\bTIME_TRAVEL\s*\('
            ],
            
            "sparksql": [
                r'\bCREATE\s+TABLE\s+.*\bUSING\s+DELTA\b',
                r'\bPARTITIONED\s+BY\s*\(',
                r'\bCLUSTER\s+BY\s*\(',
                r'\bOPTIONS\s*\(',
                r'\bMSCK\s+REPAIR\s+TABLE\b'
            ],
            
            "pyspark": [
                r'from\s+pyspark',
                r'SparkSession\.builder',
                r'\.createDataFrame\s*\(',
                r'\.spark\.sql\s*\(',
                r'\.write\.mode\s*\('
            ]
        }
    
    def register_analyzer(self, language: str, analyzer_class: Type[AnalyzerBase]) -> None:
        """
        Register an analyzer for a specific language.
        
        Args:
            language: Language identifier (e.g., 'python', 'sql', 'sas')
            analyzer_class: Analyzer class that implements AnalyzerBase
            
        Raises:
            ConfigurationError: If analyzer_class doesn't implement AnalyzerBase
        """
        if not issubclass(analyzer_class, AnalyzerBase):
            raise ConfigurationError(
                f"Analyzer class {analyzer_class.__name__} must inherit from AnalyzerBase",
                config_key="analyzer_class"
            )
        
        self._analyzers[language.lower()] = analyzer_class
        
    def unregister_analyzer(self, language: str) -> None:
        """
        Unregister an analyzer for a specific language.
        
        Args:
            language: Language identifier to remove
        """
        if language.lower() in self._analyzers:
            del self._analyzers[language.lower()]
    
    def get_analyzer(self, language: str) -> AnalyzerBase:
        """
        Get an analyzer instance for the specified language.
        
        Args:
            language: Language identifier
            
        Returns:
            Initialized analyzer instance
            
        Raises:
            UnsupportedLanguageError: If language is not supported
        """
        language_lower = language.lower()
        
        if language_lower not in self._analyzers:
            supported_languages = list(self._analyzers.keys())
            raise UnsupportedLanguageError(language, supported_languages)
        
        analyzer_class = self._analyzers[language_lower]
        return analyzer_class()
    
    def is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language: Language identifier
            
        Returns:
            True if language is supported, False otherwise
        """
        return language.lower() in self._analyzers
    
    def list_supported_languages(self) -> List[str]:
        """
        Get a list of all supported languages.
        
        Returns:
            List of supported language identifiers
        """
        return sorted(list(self._analyzers.keys()))
    
    def get_analyzer_info(self, language: str) -> Dict[str, str]:
        """
        Get information about a specific analyzer.
        
        Args:
            language: Language identifier
            
        Returns:
            Dictionary with analyzer information
            
        Raises:
            UnsupportedLanguageError: If language is not supported
        """
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language, self.list_supported_languages())
        
        analyzer_class = self._analyzers[language.lower()]
        
        return {
            "language": language.lower(),
            "class_name": analyzer_class.__name__,
            "module": analyzer_class.__module__,
            "description": analyzer_class.__doc__ or "No description available"
        }
    
    def auto_detect_language(self, code: str) -> Optional[str]:
        """
        Attempt to automatically detect the programming language of code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            Detected language identifier or None if not detected
        """
        if not code or not code.strip():
            return None
        
        # Score each language based on pattern matches
        language_scores = {}
        
        for language, patterns in self._language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
                score += matches
            
            if score > 0:
                language_scores[language] = score
        
        # Return language with highest score, or None if no matches
        if language_scores:
            return max(language_scores, key=language_scores.get)
        
        return None
    
    def analyze_with_auto_detection(self, code: str, hint_language: Optional[str] = None) -> Tuple[str, AnalyzerBase]:
        """
        Analyze code with automatic language detection.
        
        Args:
            code: Source code to analyze
            hint_language: Optional language hint to try first
            
        Returns:
            Tuple of (detected_language, analyzer_instance)
            
        Raises:
            UnsupportedLanguageError: If no language can be detected or hint is invalid
        """
        # Try hint language first if provided
        if hint_language and self.is_language_supported(hint_language):
            return hint_language.lower(), self.get_analyzer(hint_language)
        
        # Auto-detect language
        detected_language = self.auto_detect_language(code)
        
        if detected_language and self.is_language_supported(detected_language):
            return detected_language, self.get_analyzer(detected_language)
        
        # If detection fails, raise error with supported languages
        raise UnsupportedLanguageError(
            "Could not detect language",
            self.list_supported_languages()
        )


# Global registry instance
registry = AnalyzerRegistry()


# Convenience functions for common operations
def get_analyzer(language: str) -> AnalyzerBase:
    """Convenience function to get an analyzer instance."""
    return registry.get_analyzer(language)


def list_supported_languages() -> List[str]:
    """Convenience function to list supported languages."""
    return registry.list_supported_languages()


def auto_detect_language(code: str) -> Optional[str]:
    """Convenience function for language auto-detection."""
    return registry.auto_detect_language(code)


def register_custom_analyzer(language: str, analyzer_class: Type[AnalyzerBase]) -> None:
    """Convenience function to register a custom analyzer."""
    registry.register_analyzer(language, analyzer_class)

# Export the registry instance for external imports
analyzer_registry = registry
