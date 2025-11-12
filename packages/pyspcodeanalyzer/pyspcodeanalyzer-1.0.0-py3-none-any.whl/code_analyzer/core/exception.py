"""
Enterprise-Grade Exception Handling for Code Analyzer

This module provides a comprehensive exception hierarchy for the code analyzer
with specific, meaningful error types for better error diagnosis, debugging,
and professional error reporting in production environments.

Author: Code Analyzer Team
Version: 2.0.0
Date: 2025-11-11
"""

from typing import Optional, Dict, Any


class CodeAnalyzerError(Exception):
    """
    Base exception class for all code analyzer related errors.
    
    Provides a foundation for specific error types with enhanced
    error context and debugging information.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialize base exception with enhanced context.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for logging/monitoring
            context: Additional context information (file, line, etc.)
        """
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        
    def __str__(self) -> str:
        """Enhanced string representation with context."""
        base_msg = super().__str__()
        if self.error_code:
            base_msg = f"[{self.error_code}] {base_msg}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg = f"{base_msg} (Context: {context_str})"
        return base_msg


class UnsupportedLanguageError(CodeAnalyzerError):
    """
    Raised when attempting to analyze code in an unsupported language.
    
    This error indicates that the requested language analyzer is not
    available or registered in the system.
    """
    
    def __init__(self, language: str, supported_languages: Optional[list] = None):
        supported = ", ".join(supported_languages) if supported_languages else "unknown"
        message = f"Language '{language}' is not supported. Supported languages: {supported}"
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_LANG",
            context={"requested_language": language, "supported_languages": supported_languages}
        )
        self.language = language
        self.supported_languages = supported_languages


class InvalidCodeError(CodeAnalyzerError):
    """
    Raised when the provided code is malformed, invalid, or cannot be parsed.
    
    This includes syntax errors, encoding issues, or structural problems
    that prevent analysis from proceeding.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 line_number: Optional[int] = None, syntax_error: Optional[str] = None):
        context = {}
        if file_path:
            context["file_path"] = file_path
        if line_number:
            context["line_number"] = line_number
        if syntax_error:
            context["syntax_error"] = syntax_error
            
        super().__init__(
            message=message,
            error_code="INVALID_CODE",
            context=context
        )
        self.file_path = file_path
        self.line_number = line_number
        self.syntax_error = syntax_error


class ConfigurationError(CodeAnalyzerError):
    """
    Raised when there are issues with configuration files or settings.
    
    This includes missing config files, invalid YAML/JSON syntax,
    missing required parameters, or invalid configuration values.
    """
    
    def __init__(self, message: str, config_file: Optional[str] = None, 
                 config_key: Optional[str] = None, expected_type: Optional[str] = None):
        context = {}
        if config_file:
            context["config_file"] = config_file
        if config_key:
            context["config_key"] = config_key
        if expected_type:
            context["expected_type"] = expected_type
            
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            context=context
        )
        self.config_file = config_file
        self.config_key = config_key
        self.expected_type = expected_type


class AnalysisError(CodeAnalyzerError):
    """
    Raised when the analysis process fails due to internal errors.
    
    This includes regex processing failures, unexpected data structures,
    or other internal errors during the complexity analysis phase.
    """
    
    def __init__(self, message: str, analyzer_name: Optional[str] = None, 
                 phase: Optional[str] = None, original_exception: Optional[Exception] = None):
        context = {}
        if analyzer_name:
            context["analyzer"] = analyzer_name
        if phase:
            context["analysis_phase"] = phase
        if original_exception:
            context["original_error"] = str(original_exception)
            
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            context=context
        )
        self.analyzer_name = analyzer_name
        self.phase = phase
        self.original_exception = original_exception


class MetricCalculationError(CodeAnalyzerError):
    """
    Raised when metric calculation fails or produces invalid results.
    
    This includes out-of-range metric values, division by zero,
    or other mathematical errors during complexity scoring.
    """
    
    def __init__(self, message: str, metric_name: Optional[str] = None, 
                 calculated_value: Optional[Any] = None, expected_range: Optional[tuple] = None):
        context = {}
        if metric_name:
            context["metric_name"] = metric_name
        if calculated_value is not None:
            context["calculated_value"] = calculated_value
        if expected_range:
            context["expected_range"] = f"{expected_range[0]}-{expected_range[1]}"
            
        super().__init__(
            message=message,
            error_code="METRIC_ERROR",
            context=context
        )
        self.metric_name = metric_name
        self.calculated_value = calculated_value
        self.expected_range = expected_range


class FileProcessingError(CodeAnalyzerError):
    """
    Raised when file I/O operations fail during analysis.
    
    This includes file not found, permission errors, encoding issues,
    or other file system related problems.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 operation: Optional[str] = None, original_exception: Optional[Exception] = None):
        context = {}
        if file_path:
            context["file_path"] = file_path
        if operation:
            context["operation"] = operation
        if original_exception:
            context["original_error"] = str(original_exception)
            
        super().__init__(
            message=message,
            error_code="FILE_ERROR",
            context=context
        )
        self.file_path = file_path
        self.operation = operation
        self.original_exception = original_exception


class ValidationError(CodeAnalyzerError):
    """
    Raised when data validation fails.
    
    This includes invalid input parameters, out-of-range values,
    or other validation failures in user inputs or configuration.
    """
    
    def __init__(self, message: str, field_name: Optional[str] = None, 
                 field_value: Optional[Any] = None, validation_rule: Optional[str] = None):
        context = {}
        if field_name:
            context["field_name"] = field_name
        if field_value is not None:
            context["field_value"] = field_value
        if validation_rule:
            context["validation_rule"] = validation_rule
            
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context
        )
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule


# Convenience functions for common error scenarios
def raise_unsupported_language(language: str, supported_languages: list = None):
    """Convenience function to raise UnsupportedLanguageError."""
    raise UnsupportedLanguageError(language, supported_languages)


def raise_invalid_code(message: str, file_path: str = None, line_number: int = None):
    """Convenience function to raise InvalidCodeError."""
    raise InvalidCodeError(message, file_path, line_number)


def raise_configuration_error(message: str, config_file: str = None, config_key: str = None):
    """Convenience function to raise ConfigurationError."""
    raise ConfigurationError(message, config_file, config_key)


def raise_analysis_error(message: str, analyzer_name: str = None, phase: str = None):
    """Convenience function to raise AnalysisError."""
    raise AnalysisError(message, analyzer_name, phase)


def raise_metric_error(message: str, metric_name: str = None, value: Any = None):
    """Convenience function to raise MetricCalculationError."""
    raise MetricCalculationError(message, metric_name, value)
