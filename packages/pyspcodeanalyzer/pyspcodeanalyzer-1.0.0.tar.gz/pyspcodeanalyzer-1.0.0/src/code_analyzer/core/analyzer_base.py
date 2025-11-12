# src/code_analyzer/core/analyzer_base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AnalysisResult:
    language: str
    path: str
    metrics: Dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0
    classification: str = ""
    cyclomatic: float = 0.0


class AnalyzerBase(ABC):
    """
    Minimal analyzer interface. Concrete analyzers subclass this.
    """

    language: str = "base"
    default_weights: Dict[str, int] = {
        "script_size_structure": 10,
        "dependency_footprint": 10,
        "analytics_depth": 10,
        "sql_reporting_logic": 10,
        "transformation_logic": 10,
        "utility_complexity": 10,
        "execution_control": 10,
        "file_io_external_integration": 10,
        "ods_output_delivery": 10,
        "error_handling_optimization": 10,
    }
    default_classification_thresholds: Dict[str, int] = {
        "simple": 30,
        "medium": 60,
        "complex": 80,
    }
    
    def __init__(self, config: dict = None):
        self.config = config or {}

    @abstractmethod
    def analyze_source(self, source: str, path: str = "<string>") -> AnalysisResult:
        """
        Analyze the source code and return AnalysisResult.
        """
        raise NotImplementedError

    def map_score_to_label(self, score: float, thresholds: Dict) -> str:
        """
        Map total numeric score to textual classification.
        Default thresholds can be overridden in config.
        """
        # thresholds = self.config.get("classification_thresholds", {})
        # default thresholds
        t_simple = thresholds.get("simple", 30)
        t_medium = thresholds.get("medium", 60)
        t_complex = thresholds.get("complex", 80)

        if score <= t_simple:
            return "Simple"
        if score <= t_medium:
            return "Medium"
        if score <= t_complex:
            return "Complex"
        
        return "Very Complex"
    
    
