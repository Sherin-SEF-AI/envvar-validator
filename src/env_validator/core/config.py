"""
Configuration management for the env-validator package.

This module handles loading, parsing, and managing configuration
for environment variable validation.
"""

import os
import json
import yaml
import toml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from .types import (
    EnvironmentConfig,
    ValidationRule,
    ValidationType,
    EnvironmentType,
    ValidationConstraint,
    ComplianceType,
)


@dataclass
class ConfigLoader:
    """Loader for configuration files in various formats."""
    
    config_path: Optional[Path] = None
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    strict_mode: bool = False
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> EnvironmentConfig:
        """Load configuration from a dictionary."""
        schema = {}
        
        for var_name, var_config in config_dict.items():
            if isinstance(var_config, dict):
                rule = self._parse_validation_rule(var_name, var_config)
                schema[var_name] = rule
            else:
                # Simple string type specification
                rule = ValidationRule(
                    type=ValidationType(var_config),
                    required=False
                )
                schema[var_name] = rule
        
        return EnvironmentConfig(
            schema=schema,
            environment_type=self.environment,
            strict_mode=self.strict_mode
        )
    
    def load_from_file(self, file_path: Optional[Path] = None) -> EnvironmentConfig:
        """Load configuration from a file."""
        if file_path is None:
            file_path = self.config_path
        
        if file_path is None:
            raise ValueError("No configuration file path provided")
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_extension in ['.yaml', '.yml']:
                config_dict = yaml.safe_load(f)
            elif file_extension == '.json':
                config_dict = json.load(f)
            elif file_extension == '.toml':
                config_dict = toml.load(f)
            elif file_extension == '.env':
                config_dict = self._parse_dotenv_file(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_extension}")
        
        return self.load_from_dict(config_dict)
    
    def load_from_environment(self) -> EnvironmentConfig:
        """Load configuration from environment variables."""
        config_dict = {}
        
        # Look for environment variables that define the schema
        for key, value in os.environ.items():
            if key.startswith('ENV_VALIDATOR_'):
                var_name = key.replace('ENV_VALIDATOR_', '')
                config_dict[var_name] = value
        
        return self.load_from_dict(config_dict)
    
    def _parse_validation_rule(self, var_name: str, config: Dict[str, Any]) -> ValidationRule:
        """Parse a validation rule from configuration dictionary."""
        # Parse type
        type_str = config.get('type', 'str')
        try:
            validation_type = ValidationType(type_str)
        except ValueError:
            raise ValueError(f"Invalid validation type '{type_str}' for variable '{var_name}'")
        
        # Parse constraints
        constraints = []
        for constraint_name, constraint_value in config.get('constraints', {}).items():
            constraint = ValidationConstraint(
                name=constraint_name,
                value=constraint_value,
                description=config.get('description')
            )
            constraints.append(constraint)
        
        # Parse compliance requirements
        compliance = []
        for compliance_str in config.get('compliance', []):
            try:
                compliance_type = ComplianceType(compliance_str.lower())
                compliance.append(compliance_type)
            except ValueError:
                raise ValueError(f"Invalid compliance type '{compliance_str}' for variable '{var_name}'")
        
        return ValidationRule(
            type=validation_type,
            required=config.get('required', False),
            default=config.get('default'),
            validators=config.get('validators', []),
            constraints=constraints,
            sensitive=config.get('sensitive', False),
            description=config.get('description'),
            examples=config.get('examples', []),
            environments=config.get('environments'),
            compliance=compliance,
            encryption=config.get('encryption'),
            custom_validator=config.get('custom_validator')
        )
    
    def _parse_dotenv_file(self, file_obj) -> Dict[str, Any]:
        """Parse a .env file into a configuration dictionary."""
        config_dict = {}
        
        for line in file_obj:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                # Try to infer type from value
                if value.lower() in ['true', 'false']:
                    config_dict[key] = {'type': 'bool', 'default': value.lower() == 'true'}
                elif value.isdigit():
                    config_dict[key] = {'type': 'int', 'default': int(value)}
                elif value.replace('.', '').replace('-', '').isdigit():
                    config_dict[key] = {'type': 'float', 'default': float(value)}
                else:
                    config_dict[key] = {'type': 'str', 'default': value}
        
        return config_dict


@dataclass
class ConfigManager:
    """Manager for environment configurations."""
    
    configs: Dict[str, EnvironmentConfig] = field(default_factory=dict)
    current_environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    
    def add_config(self, name: str, config: EnvironmentConfig) -> None:
        """Add a configuration to the manager."""
        self.configs[name] = config
    
    def get_config(self, name: str) -> Optional[EnvironmentConfig]:
        """Get a configuration by name."""
        return self.configs.get(name)
    
    def get_current_config(self) -> Optional[EnvironmentConfig]:
        """Get the current environment configuration."""
        return self.configs.get(self.current_environment.value)
    
    def set_current_environment(self, environment: EnvironmentType) -> None:
        """Set the current environment."""
        self.current_environment = environment
    
    def merge_configs(self, base_config: EnvironmentConfig, override_config: EnvironmentConfig) -> EnvironmentConfig:
        """Merge two configurations, with override_config taking precedence."""
        merged_schema = base_config.schema.copy()
        merged_schema.update(override_config.schema)
        
        return EnvironmentConfig(
            schema=merged_schema,
            environment_type=override_config.environment_type or base_config.environment_type,
            strict_mode=override_config.strict_mode,
            allow_unknown=override_config.allow_unknown,
            auto_fix=override_config.auto_fix,
            cache_results=override_config.cache_results,
            max_cache_size=override_config.max_cache_size,
            validation_timeout=override_config.validation_timeout,
            security_scanning=override_config.security_scanning,
            compliance_checking=override_config.compliance_checking,
            monitoring_enabled=override_config.monitoring_enabled,
            log_level=override_config.log_level,
            custom_validators={**base_config.custom_validators, **override_config.custom_validators},
            template_path=override_config.template_path or base_config.template_path,
            output_format=override_config.output_format
        )
    
    def export_config(self, config: EnvironmentConfig, format: str = 'json') -> str:
        """Export configuration to a string in the specified format."""
        config_dict = self._config_to_dict(config)
        
        if format.lower() == 'json':
            return json.dumps(config_dict, indent=2, default=str)
        elif format.lower() in ['yaml', 'yml']:
            return yaml.dump(config_dict, default_flow_style=False, default_style='')
        elif format.lower() == 'toml':
            return toml.dumps(config_dict)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _config_to_dict(self, config: EnvironmentConfig) -> Dict[str, Any]:
        """Convert configuration to dictionary for export."""
        schema_dict = {}
        
        for var_name, rule in config.schema.items():
            var_config = {
                'type': rule.type.value,
                'required': rule.required,
                'sensitive': rule.sensitive,
            }
            
            if rule.default is not None:
                var_config['default'] = rule.default
            
            if rule.validators:
                var_config['validators'] = rule.validators
            
            if rule.constraints:
                var_config['constraints'] = {
                    constraint.name: constraint.value 
                    for constraint in rule.constraints
                }
            
            if rule.description:
                var_config['description'] = rule.description
            
            if rule.examples:
                var_config['examples'] = rule.examples
            
            if rule.environments:
                var_config['environments'] = rule.environments
            
            if rule.compliance:
                var_config['compliance'] = [c.value for c in rule.compliance]
            
            if rule.encryption:
                var_config['encryption'] = rule.encryption
            
            schema_dict[var_name] = var_config
        
        return {
            'environment_type': config.environment_type.value,
            'strict_mode': config.strict_mode,
            'allow_unknown': config.allow_unknown,
            'auto_fix': config.auto_fix,
            'cache_results': config.cache_results,
            'max_cache_size': config.max_cache_size,
            'validation_timeout': config.validation_timeout,
            'security_scanning': config.security_scanning,
            'compliance_checking': config.compliance_checking,
            'monitoring_enabled': config.monitoring_enabled,
            'log_level': config.log_level,
            'output_format': config.output_format,
            'schema': schema_dict
        }


# Global configuration manager instance
config_manager = ConfigManager()


def load_config(
    config_path: Optional[Union[str, Path]] = None,
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT,
    strict_mode: bool = False
) -> EnvironmentConfig:
    """Load configuration from file or environment."""
    loader = ConfigLoader(
        config_path=Path(config_path) if config_path else None,
        environment=environment,
        strict_mode=strict_mode
    )
    
    if config_path:
        return loader.load_from_file()
    else:
        return loader.load_from_environment()


def get_default_config() -> EnvironmentConfig:
    """Get a default configuration for common use cases."""
    schema = {
        "DATABASE_URL": ValidationRule(
            type=ValidationType.DATABASE_URL,
            required=True,
            description="Database connection URL",
            examples=["postgresql://user:pass@localhost/db", "sqlite:///app.db"]
        ),
        "SECRET_KEY": ValidationRule(
            type=ValidationType.SECRET,
            required=True,
            sensitive=True,
            description="Application secret key for security",
            validators=["secret_key"]
        ),
        "DEBUG": ValidationRule(
            type=ValidationType.BOOLEAN,
            default=False,
            description="Debug mode flag"
        ),
        "PORT": ValidationRule(
            type=ValidationType.PORT,
            default=8000,
            description="Application port number"
        ),
        "ALLOWED_HOSTS": ValidationRule(
            type=ValidationType.LIST,
            default=["localhost", "127.0.0.1"],
            description="List of allowed host names"
        )
    }
    
    return EnvironmentConfig(schema=schema) 