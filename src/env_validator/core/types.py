"""
Core types and enums for the env-validator package.

This module defines the fundamental data structures and types used
throughout the validation system.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path


class ValidationType(str, Enum):
    """Supported validation types for environment variables."""
    
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    LIST = "list"
    DICT = "dict"
    JSON = "json"
    FILE = "file"
    DIRECTORY = "directory"
    URL = "url"
    EMAIL = "email"
    IP_ADDRESS = "ip_address"
    PORT = "port"
    DATABASE_URL = "database_url"
    SECRET = "secret"
    API_KEY = "api_key"
    ENCRYPTION_KEY = "encryption_key"
    AWS_ARN = "aws_arn"
    GCP_PROJECT_ID = "gcp_project_id"
    AZURE_RESOURCE_ID = "azure_resource_id"


class EnvironmentType(str, Enum):
    """Environment types for different deployment stages."""
    
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    LOCAL = "local"


class ValidationLevel(str, Enum):
    """Validation levels for different types of checks."""
    
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class ComplianceType(str, Enum):
    """Compliance standards for security validation."""
    
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


@dataclass
class ValidationConstraint:
    """Represents a validation constraint for an environment variable."""
    
    name: str
    value: Any
    description: Optional[str] = None
    level: ValidationLevel = ValidationLevel.ERROR


@dataclass
class ValidationRule:
    """Represents a validation rule for an environment variable."""
    
    type: ValidationType
    required: bool = False
    default: Optional[Any] = None
    validators: List[str] = field(default_factory=list)
    constraints: List[ValidationConstraint] = field(default_factory=list)
    sensitive: bool = False
    description: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    environments: Optional[Dict[str, Union[str, Dict[str, Any]]]] = None
    compliance: List[ComplianceType] = field(default_factory=list)
    encryption: Optional[str] = None
    custom_validator: Optional[Callable] = None


@dataclass
class ValidationError:
    """Represents a validation error with detailed information."""
    
    variable_name: str
    message: str
    level: ValidationLevel = ValidationLevel.ERROR
    suggestion: Optional[str] = None
    example: Optional[str] = None
    documentation_url: Optional[str] = None
    timestamp: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationWarning:
    """Represents a validation warning with detailed information."""
    
    variable_name: str
    message: str
    suggestion: Optional[str] = None
    level: ValidationLevel = ValidationLevel.WARNING
    timestamp: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    validated_values: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    security_score: Optional[float] = None
    compliance_status: Dict[str, bool] = field(default_factory=dict)


@dataclass
class EnvironmentConfig:
    """Configuration for environment variable validation."""
    
    schema: Dict[str, ValidationRule]
    environment_type: EnvironmentType = EnvironmentType.DEVELOPMENT
    strict_mode: bool = False
    allow_unknown: bool = False
    auto_fix: bool = False
    cache_results: bool = True
    max_cache_size: int = 1000
    validation_timeout: float = 30.0
    security_scanning: bool = True
    compliance_checking: bool = True
    monitoring_enabled: bool = True
    log_level: str = "INFO"
    custom_validators: Dict[str, Callable] = field(default_factory=dict)
    template_path: Optional[Path] = None
    output_format: str = "json"


@dataclass
class HealthStatus:
    """Health status of the environment validation system."""
    
    is_healthy: bool
    status: str
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_check: Optional[str] = None
    uptime: Optional[float] = None


@dataclass
class DriftReport:
    """Report of configuration drift detection."""
    
    has_changes: bool
    changes: List[Dict[str, Any]] = field(default_factory=list)
    added_variables: List[str] = field(default_factory=list)
    removed_variables: List[str] = field(default_factory=list)
    modified_variables: List[str] = field(default_factory=list)
    severity: ValidationLevel = ValidationLevel.INFO
    timestamp: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SecurityAudit:
    """Security audit results for environment variables."""
    
    overall_score: float
    vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    risk_level: str = "LOW"
    timestamp: Optional[str] = None
    auditor_version: Optional[str] = None


# Type aliases for better code readability
ValidationSchema = Dict[str, ValidationRule]
ValidationErrors = List[ValidationError]
ValidationWarnings = List[ValidationWarning]
EnvironmentVariables = Dict[str, str]
ValidatedConfig = Dict[str, Any]
ValidatorFunction = Callable[[Any], Any]
CustomValidator = Callable[[str, Any], Union[Any, ValidationError]] 