"""
env-validator: The most comprehensive environment variable validation library for Python.

A production-ready, feature-rich library for validating environment variables
with advanced security, monitoring, and framework integration capabilities.
"""

__version__ = "1.0.0"
__author__ = "Sherin Joseph Roy"
__email__ = "sherin.joseph2217@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/Sherin-SEF-AI/env-validator"

# Core exports
from .core.validator import EnvironmentValidator, EnvironmentValidationError
from .core.types import ValidationError, ValidationWarning
from .core.config import EnvironmentConfig
from .core.types import ValidationResult
from .core.types import ValidationType, EnvironmentType

# Validator exports
from .validators.base import BaseValidator, ValidatorRegistry
from .validators.security import (
    SecretKeyValidator,
    APIKeyValidator,
    EncryptionKeyValidator,
    PasswordStrengthValidator,
)
from .validators.network import (
    URLValidator,
    IPAddressValidator,
    PortValidator,
    DatabaseURLValidator,
)
from .validators.data import (
    EmailValidator,
    JSONValidator,
    FilePathValidator,
    DirectoryPathValidator,
)
from .validators.cloud import (
    AWSARNValidator,
    GCPProjectIDValidator,
    AzureResourceIDValidator,
)

# Framework integrations
from .frameworks.django import DjangoEnvironmentValidator
from .frameworks.flask import FlaskEnvironmentValidator
from .frameworks.fastapi import FastAPIEnvironmentValidator

# Monitoring and observability
from .monitoring.health import HealthChecker, HealthStatus
from .monitoring.drift import DriftDetector, DriftReport
from .monitoring.metrics import MetricsCollector

# Security features
from .security.scanner import SecretScanner, ComplianceValidator
from .security.audit import SecurityAuditor, AuditReport

# CLI tools
from .cli.main import main as cli_main

# Utility functions
from .utils.loaders import (
    load_dotenv,
    load_yaml,
    load_json,
    load_toml,
    load_environment_file,
)
from .utils.exporters import (
    export_to_dotenv,
    export_to_yaml,
    export_to_json,
    export_to_toml,
)

# Type hints for better IDE support
__all__ = [
    # Core
    "EnvironmentValidator",
    "EnvironmentValidationError",
    "ValidationError",
    "ValidationWarning",
    "EnvironmentConfig",
    "ValidationResult",
    "ValidationType",
    "EnvironmentType",
    
    # Validators
    "BaseValidator",
    "ValidatorRegistry",
    "SecretKeyValidator",
    "APIKeyValidator",
    "EncryptionKeyValidator",
    "PasswordStrengthValidator",
    "URLValidator",
    "IPAddressValidator",
    "PortValidator",
    "DatabaseURLValidator",
    "EmailValidator",
    "JSONValidator",
    "FilePathValidator",
    "DirectoryPathValidator",
    "AWSARNValidator",
    "GCPProjectIDValidator",
    "AzureResourceIDValidator",
    
    # Frameworks
    "DjangoEnvironmentValidator",
    "FlaskEnvironmentValidator",
    "FastAPIEnvironmentValidator",
    
    # Monitoring
    "HealthChecker",
    "HealthStatus",
    "DriftDetector",
    "DriftReport",
    "MetricsCollector",
    
    # Security
    "SecretScanner",
    "ComplianceValidator",
    "SecurityAuditor",
    "AuditReport",
    
    # CLI
    "cli_main",
    
    # Utils
    "load_dotenv",
    "load_yaml",
    "load_json",
    "load_toml",
    "load_environment_file",
    "export_to_dotenv",
    "export_to_yaml",
    "export_to_json",
    "export_to_toml",
]

# Version info for compatibility checks
def get_version_info():
    """Get detailed version information."""
    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "url": __url__,
        "python_version": ">=3.8",
    }

# Initialize validator registry on import
from .validators.registry import initialize_registry
initialize_registry() 