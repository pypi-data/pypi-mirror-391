"""
Enterprise-Grade Metrics Management System

This module provides centralized metric definitions, validation, and calculations
for consistent metric handling across all analyzers with advanced analytics
and cross-language metric comparisons.

Author: Code Analyzer Team
Version: 2.0.0
Date: 2025-11-11
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from .exception import MetricCalculationError, ValidationError


class ComplexityLevel(Enum):
    """Enumeration for complexity classification levels."""
    SIMPLE = "Simple"
    MEDIUM = "Medium"
    COMPLEX = "Complex"
    VERY_COMPLEX = "Very Complex"


@dataclass
class MetricDefinition:
    """
    Definition of a complexity metric with validation rules.
    
    Attributes:
        name: Metric identifier (SAS standard naming)
        description: Human-readable metric description
        min_value: Minimum allowed value (1-4 scale for complexity assessment)
        max_value: Maximum allowed value (1-4 scale for complexity assessment)
        weight: Default weight for scoring (1-100 scale, each dimension max 10 points)
        category: Metric category for grouping
    """
    name: str
    description: str
    min_value: int = 1
    max_value: int = 4
    weight: float = 10.0  # Each dimension contributes max 10 points to total 100
    category: str = "general"
    
    def __post_init__(self):
        """Validate metric definition after initialization."""
        if self.min_value < 1 or self.min_value > 4:
            raise ValidationError(f"min_value must be 1-4, got {self.min_value}", "min_value")
        if self.max_value < 1 or self.max_value > 4:
            raise ValidationError(f"max_value must be 1-4, got {self.max_value}", "max_value")
        if self.min_value > self.max_value:
            raise ValidationError(f"min_value ({self.min_value}) cannot exceed max_value ({self.max_value})")
        if self.weight < 1 or self.weight > 10:
            raise ValidationError(f"weight must be 1-10, got {self.weight}", "weight")


class MetricRegistry:
    """
    Central registry for metric definitions with standardized SAS naming.
    
    This registry maintains the 10-dimension metric system used across
    all language analyzers for consistency and validation.
    """
    
    _instance = None
    _metrics: Dict[str, MetricDefinition] = {}
    
    def __new__(cls):
        """Singleton pattern to ensure single metrics registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize registry with standard SAS metrics."""
        if not hasattr(self, '_initialized'):
            self._initialize_standard_metrics()
            self._initialized = True
    
    def _initialize_standard_metrics(self):
        """Initialize the standard 10-dimension metric system."""
    
        # 1. Script Size & Structure
        self.register_metric(MetricDefinition(
            name="script_size_structure",
            description="Code size, number of procedures, functions, nesting depth, and structural complexity",
            category="structure",
            weight=10.0
        ))
        
        # 2. Dependency Footprint  
        self.register_metric(MetricDefinition(
            name="dependency_footprint",
            description="External dependencies, database connections, table references, and integration complexity",
            category="dependencies",
            weight=10.0
        ))
        
        # 3. Analytics Depth
        self.register_metric(MetricDefinition(
            name="analytics_depth",
            description="Advanced analytics, statistical functions, window functions, and analytical processing complexity",
            category="analytics",
            weight=10.0
        ))
        
        # 4. SQL Reporting Logic
        self.register_metric(MetricDefinition(
            name="sql_reporting_logic",
            description="SQL query complexity, joins, subqueries, and reporting logic sophistication",
            category="sql",
            weight=10.0
        ))
        
        # 5. Transformation Logic
        self.register_metric(MetricDefinition(
            name="transformation_logic",
            description="Data transformation operations, DML complexity, and data manipulation sophistication",
            category="transformation",
            weight=10.0
        ))
        
        # 6. Utility Complexity
        self.register_metric(MetricDefinition(
            name="utility_complexity",
            description="Stored procedures, functions, parameters, cursors, and utility code complexity",
            category="utility",
            weight=10.0
        ))
        
        # 7. Execution Control
        self.register_metric(MetricDefinition(
            name="execution_control",
            description="Transaction management, control flow, parallel execution, and process orchestration",
            category="execution",
            weight=10.0
        ))
        
        # 8. File I/O & External Integration
        self.register_metric(MetricDefinition(
            name="file_io_external_integration",
            description="File operations, external system integration, APIs, and I/O complexity",
            category="integration",
            weight=10.0
        ))
        
        # 9. ODS Output Delivery
        self.register_metric(MetricDefinition(
            name="ods_output_delivery",
            description="Output generation, result sets, reporting delivery, and presentation complexity",
            category="output",
            weight=10.0
        ))
        
        # 10. Error Handling & Optimization
        self.register_metric(MetricDefinition(
            name="error_handling_optimization",
            description="Exception handling, performance optimization, security, and code quality measures",
            category="quality",
            weight=10.0
        ))
    
    def register_metric(self, metric_def: MetricDefinition) -> None:
        """
        Register a metric definition.
        
        Args:
            metric_def: MetricDefinition instance
        """
        self._metrics[metric_def.name] = metric_def
    
    def get_metric(self, name: str) -> MetricDefinition:
        """
        Get a metric definition by name.
        
        Args:
            name: Metric name
            
        Returns:
            MetricDefinition instance
            
        Raises:
            ValidationError: If metric name is not found
        """
        if name not in self._metrics:
            raise ValidationError(f"Unknown metric: {name}", "metric_name")
        return self._metrics[name]
    
    def list_metrics(self) -> List[str]:
        """Get list of all registered metric names."""
        return list(self._metrics.keys())
    
    def list_standard_metrics(self) -> List[str]:
        """Get list of the 10 standard SAS metrics."""
        return [
            "script_size_structure",
            "dependency_footprint", 
            "analytics_depth",
            "sql_reporting_logic",
            "transformation_logic",
            "utility_complexity",
            "execution_control",
            "file_io_external_integration",
            "ods_output_delivery",
            "error_handling_optimization"
        ]
    
    def get_metrics_by_category(self, category: str) -> List[MetricDefinition]:
        """Get all metrics in a specific category."""
        return [metric for metric in self._metrics.values() if metric.category == category]
    
    def get_default_weights(self) -> Dict[str, float]:
        """Get default weights from all registered metrics."""
        weights = {}
        for metric_name in self.list_standard_metrics():
            metric_def = self.get_metric(metric_name)
            weights[metric_name] = metric_def.weight
        return weights
    
    def get_default_thresholds(self) -> Dict[str, int]:
        """Get default classification thresholds for backward compatibility."""
        # Map ComplexityLevel thresholds to legacy format for analyzers
        return {
            "simple": 30,      # 1-30 → Simple
            "medium": 60,      # 31-60 → Medium  
            "complex": 80,     # 60-80 → Comple
                               # 80-100 → Very Complex
        }


class MetricValidator:
    """
    Validator for metric values and complexity calculations.
    
    Provides validation, normalization, and scoring utilities
    for enterprise-grade metric consistency.
    """
    
    def __init__(self, metric_registry: Optional[MetricRegistry] = None):
        """Initialize validator with metric registry."""
        self.registry = metric_registry or MetricRegistry()
    
    def validate_metric_value(self, metric_name: str, value: Any) -> int:
        """
        Validate a metric value against its definition.
        
        Args:
            metric_name: Name of the metric
            value: Value to validate
            
        Returns:
            Validated integer value (1-4)
            
        Raises:
            MetricCalculationError: If value is invalid
        """
        metric_def = self.registry.get_metric(metric_name)
        
        # Convert to integer
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise MetricCalculationError(
                f"Metric value must be numeric, got {type(value).__name__}: {value}",
                metric_name=metric_name,
                calculated_value=value
            )
        
        # Check range
        if int_value < metric_def.min_value or int_value > metric_def.max_value:
            raise MetricCalculationError(
                f"Metric value {int_value} out of range [{metric_def.min_value}-{metric_def.max_value}]",
                metric_name=metric_name,
                calculated_value=int_value,
                expected_range=(metric_def.min_value, metric_def.max_value)
            )
        
        return int_value
    
    def validate_all_metrics(self, metrics: Dict[str, Any]) -> Dict[str, int]:
        """
        Validate all metrics in a dictionary.
        
        Args:
            metrics: Dictionary of metric_name -> value
            
        Returns:
            Dictionary of validated metrics
            
        Raises:
            MetricCalculationError: If any metric is invalid
        """
        validated = {}
        
        for metric_name, value in metrics.items():
            validated[metric_name] = self.validate_metric_value(metric_name, value)
        
        return validated
    
    def calculate_total_score(self, metrics: Dict[str, int], weights: Optional[Dict[str, float]] = None) -> int:
        """
        Calculate total complexity score from individual metrics.
        
        Args:
            metrics: Dictionary of metric_name -> value (1-4)
            weights: Optional custom weights (1-10 points per dimension)
            
        Returns:
            Total score (0-100 points)
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        # Validate all metrics first
        validated_metrics = self.validate_all_metrics(metrics)
        
        # Use default weights from registry if not provided
        if weights is None:
            weights = {}
            for metric_name in validated_metrics.keys():
                metric_def = self.registry.get_metric(metric_name)
                weights[metric_name] = metric_def.weight
        
        # Calculate weighted sum
        total = 0
        
        for metric_name, value in validated_metrics.items():
            weight = weights.get(metric_name, 10.0)  # Default 10 points per dimension
            
            # Convert 1-4 complexity to 0.25-1.0 multiplier, then multiply by weight
            # 1 (Simple) = 25% of max points, 4 (Very Complex) = 100% of max points
            multiplier = (value - 1) / 3.0 * 0.75 + 0.25  # Maps 1->0.25, 2->0.5, 3->0.75, 4->1.0
            dimension_score = weight * multiplier
            total += dimension_score
        
        # Ensure score is in valid range
        total_score = max(0, min(100, int(total)))
        
        return total_score
    
    def classify_complexity(self, total_score: int) -> ComplexityLevel:
        """
        Classify complexity level based on total score.
        
        Args:
            total_score: Total complexity score (0-100)
            
        Returns:
            ComplexityLevel enum value
            
        Raises:
            MetricCalculationError: If score is out of range
        """
        if total_score < 0 or total_score > 100:
            raise MetricCalculationError(
                f"Total score {total_score} out of range [0-100]",
                calculated_value=total_score,
                expected_range=(0, 100)
            )
        
        if total_score <= 30:
            return ComplexityLevel.SIMPLE
        elif total_score <= 60:
            return ComplexityLevel.MEDIUM
        elif total_score <= 80:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.VERY_COMPLEX
    
    def get_metric_statistics(self, metrics: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate statistics for a set of metrics.
        
        Args:
            metrics: Dictionary of metric_name -> value
            
        Returns:
            Dictionary with statistics
        """
        validated_metrics = self.validate_all_metrics(metrics)
        values = list(validated_metrics.values())
        
        if not values:
            return {"count": 0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values)
        }


# Global instances
metric_registry = MetricRegistry()
metric_validator = MetricValidator(metric_registry)


# Convenience functions
def validate_metric_value(metric_name: str, value: Any) -> int:
    """Convenience function to validate a single metric value."""
    return metric_validator.validate_metric_value(metric_name, value)


def calculate_total_score(metrics: Dict[str, int]) -> int:
    """Convenience function to calculate total complexity score."""
    return metric_validator.calculate_total_score(metrics)


def classify_complexity(total_score: int) -> ComplexityLevel:
    """Convenience function to classify complexity level."""
    return metric_validator.classify_complexity(total_score)


def get_standard_metrics() -> List[str]:
    """Convenience function to get standard metric names."""
    return metric_registry.list_standard_metrics()


def get_registry_weights() -> Dict[str, float]:
    """Convenience function to get default weights from registry."""
    return metric_registry.get_default_weights()


def get_registry_thresholds() -> Dict[str, int]:
    """Convenience function to get default thresholds from registry."""
    return metric_registry.get_default_thresholds()
