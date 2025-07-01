"""
Core validation engine for the env-validator package.

This module contains the main EnvironmentValidator class and related
validation logic for environment variables.
"""

import os
import time
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from functools import lru_cache

from .types import (
    EnvironmentConfig,
    ValidationRule,
    ValidationResult,
    ValidationError,
    ValidationWarning,
    ValidationType,
    EnvironmentType,
    ValidationLevel,
)
from .config import ConfigLoader


class EnvironmentValidationError(Exception):
    """Exception raised when environment validation fails."""
    
    def __init__(self, message: str, errors: List[ValidationError] = None, warnings: List[ValidationWarning] = None):
        super().__init__(message)
        self.errors = errors or []
        self.warnings = warnings or []


@dataclass
class ValidationContext:
    """Context for validation operations."""
    
    environment_type: EnvironmentType
    strict_mode: bool = False
    auto_fix: bool = False
    cache_results: bool = True
    validation_timeout: float = 30.0
    security_scanning: bool = True
    compliance_checking: bool = True
    custom_validators: Dict[str, Any] = field(default_factory=dict)


class EnvironmentValidator:
    """
    Main validator class for environment variables.
    
    This class provides comprehensive validation capabilities for environment
    variables with support for type checking, custom validators, security
    scanning, and compliance checking.
    """
    
    def __init__(
        self,
        schema: Union[Dict[str, Any], EnvironmentConfig],
        environment_type: EnvironmentType = EnvironmentType.DEVELOPMENT,
        strict_mode: bool = False,
        auto_fix: bool = False,
        cache_results: bool = True,
        validation_timeout: float = 30.0,
        security_scanning: bool = True,
        compliance_checking: bool = True,
        custom_validators: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the environment validator.
        
        Args:
            schema: Validation schema or configuration
            environment_type: Type of environment being validated
            strict_mode: Whether to use strict validation mode
            auto_fix: Whether to attempt automatic fixes
            cache_results: Whether to cache validation results
            validation_timeout: Timeout for validation operations
            security_scanning: Whether to perform security scanning
            compliance_checking: Whether to perform compliance checking
            custom_validators: Custom validator functions
            logger: Logger instance for validation operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.custom_validators = custom_validators or {}
        
        # Parse schema
        if isinstance(schema, dict):
            self.config = self._create_config_from_schema(schema, environment_type, strict_mode)
        else:
            self.config = schema
        
        # Create validation context
        self.context = ValidationContext(
            environment_type=environment_type,
            strict_mode=strict_mode,
            auto_fix=auto_fix,
            cache_results=cache_results,
            validation_timeout=validation_timeout,
            security_scanning=security_scanning,
            compliance_checking=compliance_checking,
            custom_validators=self.custom_validators
        )
        
        # Initialize caches
        self._validation_cache = {}
        self._type_converter_cache = {}
        
        self.logger.info(f"EnvironmentValidator initialized for {environment_type.value} environment")
    
    def validate(self, env_vars: Optional[Dict[str, str]] = None) -> ValidationResult:
        """
        Validate environment variables against the schema.
        
        Args:
            env_vars: Environment variables to validate (uses os.environ if None)
            
        Returns:
            ValidationResult containing validation results
            
        Raises:
            EnvironmentValidationError: If validation fails and strict mode is enabled
        """
        start_time = time.time()
        
        # Get environment variables
        if env_vars is None:
            env_vars = dict(os.environ)
        
        self.logger.info(f"Starting validation of {len(env_vars)} environment variables")
        
        # Initialize result
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            validated_values={},
            metadata={
                'environment_type': self.context.environment_type.value,
                'strict_mode': self.context.strict_mode,
                'total_variables': len(env_vars),
                'schema_variables': len(self.config.schema)
            }
        )
        
        try:
            # Validate each variable in the schema
            for var_name, rule in self.config.schema.items():
                validation_result = self._validate_variable(var_name, rule, env_vars)
                
                if isinstance(validation_result, ValidationError):
                    result.errors.append(validation_result)
                    result.is_valid = False
                elif isinstance(validation_result, ValidationWarning):
                    result.warnings.append(validation_result)
                else:
                    result.validated_values[var_name] = validation_result
            
            # Check for unknown variables if not allowed
            if not self.config.allow_unknown:
                unknown_vars = set(env_vars.keys()) - set(self.config.schema.keys())
                if unknown_vars:
                    for var_name in unknown_vars:
                        error = ValidationError(
                            variable_name=var_name,
                            message=f"Unknown environment variable '{var_name}'",
                            suggestion="Add this variable to your validation schema or set allow_unknown=True",
                            level=ValidationLevel.WARNING if not self.context.strict_mode else ValidationLevel.ERROR
                        )
                        if self.context.strict_mode:
                            result.errors.append(error)
                            result.is_valid = False
                        else:
                            result.warnings.append(ValidationWarning(
                                variable_name=var_name,
                                message=error.message,
                                suggestion=error.suggestion
                            ))
            
            # Perform security scanning if enabled
            if self.context.security_scanning:
                security_result = self._perform_security_scan(result.validated_values)
                result.security_score = security_result.get('score')
                result.metadata['security_scan'] = security_result
            
            # Perform compliance checking if enabled
            if self.context.compliance_checking:
                compliance_result = self._perform_compliance_check(result.validated_values)
                result.compliance_status = compliance_result.get('status', {})
                result.metadata['compliance_check'] = compliance_result
            
            # Calculate performance metrics
            result.performance_metrics = {
                'validation_time': time.time() - start_time,
                'variables_validated': len(result.validated_values),
                'errors_count': len(result.errors),
                'warnings_count': len(result.warnings)
            }
            
            self.logger.info(f"Validation completed in {result.performance_metrics['validation_time']:.3f}s")
            
            return result
            
        except EnvironmentValidationError:
            # Re-raise our own validation errors in strict mode
            raise
        except Exception as e:
            self.logger.error(f"Validation failed with unexpected error: {e}")
            result.is_valid = False
            result.errors.append(ValidationError(
                variable_name="SYSTEM",
                message=f"Unexpected validation error: {str(e)}",
                level=ValidationLevel.ERROR
            ))
            return result
    
    def _validate_variable(
        self,
        var_name: str,
        rule: ValidationRule,
        env_vars: Dict[str, str]
    ) -> Union[Any, ValidationError, ValidationWarning]:
        """Validate a single environment variable."""
        
        # Check if variable exists
        if var_name not in env_vars:
            if rule.required:
                return ValidationError(
                    variable_name=var_name,
                    message=f"Required environment variable '{var_name}' is not set",
                    suggestion="Set this environment variable or provide a default value",
                    example=rule.examples[0] if rule.examples else None
                )
            elif rule.default is not None:
                return rule.default
            else:
                return None
        
        raw_value = env_vars[var_name]
        
        # Convert type
        try:
            converted_value = self._convert_type(raw_value, rule.type)
        except (ValueError, TypeError) as e:
            return ValidationError(
                variable_name=var_name,
                message=f"Failed to convert '{raw_value}' to {rule.type.value}: {str(e)}",
                suggestion=f"Provide a valid {rule.type.value} value",
                example=rule.examples[0] if rule.examples else None
            )
        
        # Apply custom validators
        for validator_name in rule.validators:
            try:
                converted_value = self._apply_validator(validator_name, converted_value, rule)
            except Exception as e:
                return ValidationError(
                    variable_name=var_name,
                    message=f"Validator '{validator_name}' failed: {str(e)}",
                    suggestion="Check the validator documentation for requirements"
                )
        
        # Apply constraints
        for constraint in rule.constraints:
            if not self._check_constraint(converted_value, constraint):
                return ValidationError(
                    variable_name=var_name,
                    message=f"Constraint '{constraint.name}' failed for value '{converted_value}'",
                    suggestion=constraint.description or f"Value must satisfy constraint: {constraint.name}"
                )
        
        # Apply custom validator function
        if rule.custom_validator:
            try:
                converted_value = rule.custom_validator(converted_value)
            except Exception as e:
                return ValidationError(
                    variable_name=var_name,
                    message=f"Custom validator failed: {str(e)}",
                    suggestion="Check your custom validator implementation"
                )
        
        return converted_value
    
    def _convert_type(self, value: str, target_type: ValidationType) -> Any:
        """Convert a string value to the target type."""
        
        # Check cache first
        cache_key = (value, target_type)
        if cache_key in self._type_converter_cache:
            return self._type_converter_cache[cache_key]
        
        try:
            if target_type == ValidationType.STRING:
                converted = str(value)
            elif target_type == ValidationType.INTEGER:
                converted = int(value)
            elif target_type == ValidationType.FLOAT:
                converted = float(value)
            elif target_type == ValidationType.BOOLEAN:
                converted = self._parse_boolean(value)
            elif target_type == ValidationType.LIST:
                converted = self._parse_list(value)
            elif target_type == ValidationType.DICT:
                converted = self._parse_dict(value)
            elif target_type == ValidationType.JSON:
                converted = self._parse_json(value)
            else:
                # For specialized types, return as string for now
                # Validators will handle the specific validation
                converted = str(value)
            
            # Cache the result
            if self.context.cache_results:
                self._type_converter_cache[cache_key] = converted
            
            return converted
            
        except Exception as e:
            raise ValueError(f"Failed to convert '{value}' to {target_type.value}: {str(e)}")
    
    def _parse_boolean(self, value: str) -> bool:
        """Parse a boolean value from string."""
        value_lower = value.lower()
        if value_lower in ('true', '1', 'yes', 'on', 'enabled'):
            return True
        elif value_lower in ('false', '0', 'no', 'off', 'disabled'):
            return False
        else:
            raise ValueError(f"Invalid boolean value: {value}")
    
    def _parse_list(self, value: str) -> List[str]:
        """Parse a list value from string."""
        # Support multiple delimiters
        if ',' in value:
            return [item.strip() for item in value.split(',')]
        elif ';' in value:
            return [item.strip() for item in value.split(';')]
        elif '|' in value:
            return [item.strip() for item in value.split('|')]
        else:
            return [value.strip()]
    
    def _parse_dict(self, value: str) -> Dict[str, str]:
        """Parse a dictionary value from string."""
        # Support key=value format
        result = {}
        for item in value.split(','):
            if '=' in item:
                key, val = item.split('=', 1)
                result[key.strip()] = val.strip()
        return result
    
    def _parse_json(self, value: str) -> Any:
        """Parse a JSON value from string."""
        import json
        return json.loads(value)
    
    def _apply_validator(self, validator_name: str, value: Any, rule: ValidationRule) -> Any:
        """Apply a validator to a value."""
        # This will be implemented when we create the validators module
        # For now, return the value unchanged
        return value
    
    def _check_constraint(self, value: Any, constraint: Any) -> bool:
        """Check if a value satisfies a constraint."""
        # This will be implemented when we create the constraints module
        # For now, return True
        return True
    
    def _perform_security_scan(self, validated_values: Dict[str, Any]) -> Dict[str, Any]:
        """Perform security scanning on validated values."""
        # This will be implemented when we create the security module
        return {'score': 100.0, 'issues': []}
    
    def _perform_compliance_check(self, validated_values: Dict[str, Any]) -> Dict[str, Any]:
        """Perform compliance checking on validated values."""
        # This will be implemented when we create the compliance module
        return {'status': {}, 'issues': []}
    
    def _create_config_from_schema(
        self,
        schema: Dict[str, Any],
        environment_type: EnvironmentType,
        strict_mode: bool
    ) -> EnvironmentConfig:
        """Create a configuration from a schema dictionary."""
        # Convert schema to ValidationRule objects
        rules = {}
        for var_name, var_config in schema.items():
            if isinstance(var_config, dict):
                rule = ValidationRule(
                    type=ValidationType(var_config.get('type', 'str')),
                    required=var_config.get('required', False),
                    default=var_config.get('default'),
                    validators=var_config.get('validators', []),
                    sensitive=var_config.get('sensitive', False),
                    description=var_config.get('description'),
                    examples=var_config.get('examples', [])
                )
            else:
                rule = ValidationRule(
                    type=ValidationType(var_config),
                    required=False
                )
            rules[var_name] = rule
        
        return EnvironmentConfig(
            schema=rules,
            environment_type=environment_type,
            strict_mode=strict_mode
        )
    
    def get_validated_config(self) -> Dict[str, Any]:
        """Get the validated configuration as a dictionary."""
        result = self.validate()
        return result.validated_values
    
    def check_health(self) -> bool:
        """Check if the validator is healthy."""
        try:
            result = self.validate()
            return result.is_valid
        except Exception:
            return False
    
    def clear_cache(self) -> None:
        """Clear the validation cache."""
        self._validation_cache.clear()
        self._type_converter_cache.clear()
        self.logger.info("Validation cache cleared") 