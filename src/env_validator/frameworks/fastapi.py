"""
FastAPI framework integration for env-validator.
"""

from typing import Any, Dict, Optional
from ..core.validator import EnvironmentValidator
from ..core.types import EnvironmentConfig, ValidationResult


class FastAPIEnvironmentValidator(EnvironmentValidator):
    """FastAPI-specific environment validator with Pydantic integration."""
    
    def __init__(self, schema: Dict[str, Any], **kwargs):
        super().__init__(schema, **kwargs)
    
    def validate_fastapi_config(self) -> ValidationResult:
        """Validate FastAPI-specific environment variables."""
        # Add FastAPI-specific validation logic here
        return self.validate()
    
    def create_pydantic_settings(self, config: Dict[str, Any]) -> Any:
        """Create Pydantic settings from validated environment variables."""
        # This would integrate with Pydantic BaseSettings
        return config 