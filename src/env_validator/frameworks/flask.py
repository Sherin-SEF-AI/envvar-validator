"""
Flask framework integration for env-validator.
"""

from typing import Any, Dict, Optional
from ..core.validator import EnvironmentValidator
from ..core.types import EnvironmentConfig, ValidationResult


class FlaskEnvironmentValidator(EnvironmentValidator):
    """Flask-specific environment validator with app configuration."""
    
    def __init__(self, schema: Dict[str, Any], **kwargs):
        super().__init__(schema, **kwargs)
    
    def validate_flask_config(self) -> ValidationResult:
        """Validate Flask-specific environment variables."""
        # Add Flask-specific validation logic here
        return self.validate()
    
    def configure_flask_app(self, app, config: Dict[str, Any]) -> None:
        """Configure Flask app with validated environment variables."""
        for key, value in config.items():
            app.config[key] = value 