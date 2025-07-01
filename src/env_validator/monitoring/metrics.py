"""
Metrics collection for env-validator.
"""

from typing import Dict, Any


class MetricsCollector:
    """Collector for environment validation metrics."""
    
    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        """Get current metrics."""
        return {
            "validation_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "average_validation_time": 0.0,
        } 