"""
Django framework integration for env-validator.
"""

from typing import Any, Dict, Optional
from ..core.validator import EnvironmentValidator
from ..core.types import EnvironmentConfig, ValidationResult


class DjangoEnvironmentValidator(EnvironmentValidator):
    """Django-specific environment validator with settings integration."""
    
    def __init__(self, schema: Dict[str, Any], **kwargs):
        super().__init__(schema, **kwargs)
    
    def validate_django_settings(self) -> ValidationResult:
        """Validate Django-specific environment variables."""
        # Add Django-specific validation logic here
        return self.validate()
    
    def parse_database_url(self, database_url: str) -> Dict[str, Any]:
        """Parse database URL for Django DATABASES setting."""
        # Basic database URL parsing
        if database_url.startswith('sqlite:///'):
            return {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': database_url.replace('sqlite:///', ''),
            }
        elif database_url.startswith('postgresql://'):
            # Parse PostgreSQL URL
            return {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'database_name',  # Extract from URL
                'USER': 'user',  # Extract from URL
                'PASSWORD': 'password',  # Extract from URL
                'HOST': 'localhost',  # Extract from URL
                'PORT': '5432',  # Extract from URL
            }
        else:
            raise ValueError(f"Unsupported database URL format: {database_url}") 