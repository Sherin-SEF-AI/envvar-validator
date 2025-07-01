"""
Base validator classes and registry for the env-validator package.

This module provides the foundation for all validators in the system,
including the BaseValidator class and ValidatorRegistry for managing
validator instances.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Type
from dataclasses import dataclass, field


@dataclass
class ValidationContext:
    """Context information for validation operations."""
    
    variable_name: str
    environment_type: str
    strict_mode: bool = False
    custom_validators: Dict[str, Callable] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ValidationError(Exception):
    """Exception raised when validation fails."""
    
    def __init__(
        self,
        message: str,
        variable_name: Optional[str] = None,
        suggestion: Optional[str] = None,
        example: Optional[str] = None,
        documentation_url: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.variable_name = variable_name
        self.suggestion = suggestion
        self.example = example
        self.documentation_url = documentation_url
        self.context = context or {}


class BaseValidator(ABC):
    """
    Base class for all validators in the env-validator system.
    
    This class provides the foundation for creating custom validators
    and defines the interface that all validators must implement.
    """
    
    def __init__(self, name: Optional[str] = None, **kwargs):
        """
        Initialize the validator.
        
        Args:
            name: Optional name for the validator
            **kwargs: Additional configuration options
        """
        self.name = name or self.__class__.__name__
        self.config = kwargs
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
    
    @abstractmethod
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> Any:
        """
        Validate a value.
        
        Args:
            value: The value to validate
            context: Optional validation context
            
        Returns:
            The validated value (may be modified)
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    def __call__(self, value: Any, context: Optional[ValidationContext] = None) -> Any:
        """Make the validator callable."""
        return self.validate(value, context)
    
    def get_description(self) -> str:
        """Get a description of what this validator does."""
        return getattr(self, '__doc__', f"Validator: {self.name}")
    
    def get_examples(self) -> List[str]:
        """Get example values that would pass validation."""
        return getattr(self, 'examples', [])
    
    def get_suggestions(self) -> List[str]:
        """Get suggestions for fixing common validation issues."""
        return getattr(self, 'suggestions', [])


class ValidatorRegistry:
    """
    Registry for managing validator instances.
    
    This class provides a centralized way to register, retrieve, and manage
    validators throughout the system.
    """
    
    def __init__(self):
        """Initialize the validator registry."""
        self._validators: Dict[str, Type[BaseValidator]] = {}
        self._instances: Dict[str, BaseValidator] = {}
        self.logger = logging.getLogger(f"{__name__}.ValidatorRegistry")
    
    def register(self, name: str, validator_class: Type[BaseValidator]) -> None:
        """
        Register a validator class.
        
        Args:
            name: Name to register the validator under
            validator_class: The validator class to register
        """
        if not issubclass(validator_class, BaseValidator):
            raise ValueError(f"Validator class must inherit from BaseValidator: {validator_class}")
        
        self._validators[name] = validator_class
        self.logger.info(f"Registered validator: {name} -> {validator_class.__name__}")
    
    def register_instance(self, name: str, validator_instance: BaseValidator) -> None:
        """
        Register a validator instance.
        
        Args:
            name: Name to register the validator under
            validator_instance: The validator instance to register
        """
        if not isinstance(validator_instance, BaseValidator):
            raise ValueError(f"Validator instance must be a BaseValidator: {type(validator_instance)}")
        
        self._instances[name] = validator_instance
        self.logger.info(f"Registered validator instance: {name} -> {validator_instance.name}")
    
    def get(self, name: str) -> Optional[BaseValidator]:
        """
        Get a validator by name.
        
        Args:
            name: Name of the validator to retrieve
            
        Returns:
            The validator instance or None if not found
        """
        # Check instances first
        if name in self._instances:
            return self._instances[name]
        
        # Check classes and create instance
        if name in self._validators:
            validator_class = self._validators[name]
            instance = validator_class()
            self._instances[name] = instance
            return instance
        
        return None
    
    def get_class(self, name: str) -> Optional[Type[BaseValidator]]:
        """
        Get a validator class by name.
        
        Args:
            name: Name of the validator class to retrieve
            
        Returns:
            The validator class or None if not found
        """
        return self._validators.get(name)
    
    def list_validators(self) -> List[str]:
        """
        Get a list of all registered validator names.
        
        Returns:
            List of validator names
        """
        return list(set(self._validators.keys()) | set(self._instances.keys()))
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a validator.
        
        Args:
            name: Name of the validator to unregister
            
        Returns:
            True if the validator was unregistered, False if not found
        """
        removed = False
        
        if name in self._validators:
            del self._validators[name]
            removed = True
        
        if name in self._instances:
            del self._instances[name]
            removed = True
        
        if removed:
            self.logger.info(f"Unregistered validator: {name}")
        
        return removed
    
    def clear(self) -> None:
        """Clear all registered validators."""
        self._validators.clear()
        self._instances.clear()
        self.logger.info("Cleared all registered validators")


# Global validator registry instance
validator_registry = ValidatorRegistry()


def register_validator(name: str, validator_class: Type[BaseValidator]) -> None:
    """
    Register a validator class with the global registry.
    
    Args:
        name: Name to register the validator under
        validator_class: The validator class to register
    """
    validator_registry.register(name, validator_class)


def get_validator(name: str) -> Optional[BaseValidator]:
    """
    Get a validator from the global registry.
    
    Args:
        name: Name of the validator to retrieve
        
    Returns:
        The validator instance or None if not found
    """
    return validator_registry.get(name)


def list_validators() -> List[str]:
    """
    Get a list of all registered validators.
    
    Returns:
        List of validator names
    """
    return validator_registry.list_validators()


# Decorator for easy validator registration
def validator(name: str):
    """
    Decorator to register a validator class.
    
    Args:
        name: Name to register the validator under
    """
    def decorator(cls: Type[BaseValidator]) -> Type[BaseValidator]:
        register_validator(name, cls)
        return cls
    return decorator 