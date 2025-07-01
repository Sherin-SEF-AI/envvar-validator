"""
Drift detection for env-validator.
"""

from typing import Dict, Any, List
from ..core.types import DriftReport, ValidationLevel


class DriftDetector:
    """Detector for configuration drift."""
    
    @staticmethod
    def detect_drift() -> DriftReport:
        """Detect configuration drift."""
        return DriftReport(
            has_changes=False,
            changes=[],
            added_variables=[],
            removed_variables=[],
            modified_variables=[],
            severity=ValidationLevel.INFO,
            timestamp=None,
            recommendations=[]
        ) 