"""
Validator registry initialization for the env-validator package.

This module initializes the validator registry with all built-in validators
and provides functions for managing the registry.
"""

import logging
from typing import Dict, List, Optional

from .base import ValidatorRegistry, register_validator, validator_registry


def initialize_registry() -> None:
    """Initialize the validator registry with all built-in validators."""
    logger = logging.getLogger(__name__)
    logger.info("Initializing validator registry...")
    
    # Import all validator modules to register them
    try:
        # Security validators
        from .security import (
            SecretKeyValidator,
            APIKeyValidator,
            EncryptionKeyValidator,
            PasswordStrengthValidator,
        )
        
        # Network validators
        from .network import (
            URLValidator,
            IPAddressValidator,
            PortValidator,
            DatabaseURLValidator,
        )
        
        # Data validators
        from .data import (
            EmailValidator,
            JSONValidator,
            FilePathValidator,
            DirectoryPathValidator,
        )
        
        # Cloud validators
        from .cloud import (
            AWSARNValidator,
            GCPProjectIDValidator,
            AzureResourceIDValidator,
        )
        
        logger.info("All validator modules imported successfully")
        
    except ImportError as e:
        logger.warning(f"Some validator modules could not be imported: {e}")
    
    logger.info(f"Validator registry initialized with {len(validator_registry.list_validators())} validators")


def get_registry() -> ValidatorRegistry:
    """Get the global validator registry instance."""
    return validator_registry


def register_custom_validator(name: str, validator_class) -> None:
    """
    Register a custom validator with the registry.
    
    Args:
        name: Name to register the validator under
        validator_class: The validator class to register
    """
    register_validator(name, validator_class)


def get_available_validators() -> List[str]:
    """
    Get a list of all available validators.
    
    Returns:
        List of validator names
    """
    return validator_registry.list_validators()


def get_validator_info(name: str) -> Optional[Dict]:
    """
    Get information about a specific validator.
    
    Args:
        name: Name of the validator
        
    Returns:
        Dictionary with validator information or None if not found
    """
    validator = validator_registry.get(name)
    if validator is None:
        return None
    
    return {
        'name': validator.name,
        'description': validator.get_description(),
        'examples': validator.get_examples(),
        'suggestions': validator.get_suggestions(),
        'class': validator.__class__.__name__,
    }


def clear_registry() -> None:
    """Clear all validators from the registry."""
    validator_registry.clear()


# Initialize the registry when this module is imported
initialize_registry() 