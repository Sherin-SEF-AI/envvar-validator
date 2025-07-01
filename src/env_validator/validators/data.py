"""
Data validators for the env-validator package.

This module provides validators for data-related environment variables,
including email validation, JSON validation, file path validation, and
directory path validation.
"""

import json
import re
import os
from pathlib import Path
from typing import Any, Optional, Dict, List
from email_validator import validate_email, EmailNotValidError

from .base import BaseValidator, ValidationError, ValidationContext, validator


@validator("email")
class EmailValidator(BaseValidator):
    """
    Validator for email addresses with RFC-compliant validation.
    
    This validator ensures that email addresses are properly formatted
    according to RFC standards and optionally checks domain validity.
    """
    
    def __init__(
        self,
        check_deliverability: bool = False,
        allow_empty: bool = False,
        **kwargs
    ):
        """
        Initialize the email validator.
        
        Args:
            check_deliverability: Whether to check if email domain is deliverable
            allow_empty: Whether to allow empty email addresses
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.check_deliverability = check_deliverability
        self.allow_empty = allow_empty
        
        self.examples = [
            "user@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "user123@subdomain.example.com"
        ]
        self.suggestions = [
            "Use a valid email format (user@domain.com)",
            "Check for typos in the email address",
            "Ensure the domain exists and is valid",
            "Use a professional email address for business applications"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate an email address.
        
        Args:
            value: The email address to validate
            context: Optional validation context
            
        Returns:
            The validated email address
            
        Raises:
            ValidationError: If the email address doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Email must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check for empty email
        if not value.strip():
            if self.allow_empty:
                return value
            else:
                raise ValidationError(
                    "Email address cannot be empty",
                    variable_name=context.variable_name if context else None,
                    suggestion="Provide a valid email address"
                )
        
        # Validate email format
        try:
            email_info = validate_email(value, check_deliverability=self.check_deliverability)
            normalized_email = email_info.normalized
        except EmailNotValidError as e:
            raise ValidationError(
                f"Invalid email address: {str(e)}",
                variable_name=context.variable_name if context else None,
                suggestion="Check email format and ensure domain is valid"
            )
        
        return normalized_email


@validator("json")
class JSONValidator(BaseValidator):
    """
    Validator for JSON strings with schema validation support.
    
    This validator ensures that JSON strings are properly formatted
    and optionally validates against a JSON schema.
    """
    
    def __init__(
        self,
        schema: Optional[Dict] = None,
        allow_empty: bool = False,
        **kwargs
    ):
        """
        Initialize the JSON validator.
        
        Args:
            schema: Optional JSON schema for validation
            allow_empty: Whether to allow empty JSON strings
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.schema = schema
        self.allow_empty = allow_empty
        
        self.examples = [
            '{"key": "value"}',
            '{"name": "John", "age": 30, "active": true}',
            '[1, 2, 3, 4, 5]',
            '{"config": {"debug": false, "port": 8080}}'
        ]
        self.suggestions = [
            "Use valid JSON format",
            "Check for missing quotes around string values",
            "Ensure all brackets and braces are properly closed",
            "Use a JSON validator tool to check syntax"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> Any:
        """
        Validate a JSON string.
        
        Args:
            value: The JSON string to validate
            context: Optional validation context
            
        Returns:
            The parsed JSON object
            
        Raises:
            ValidationError: If the JSON doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"JSON must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check for empty JSON
        if not value.strip():
            if self.allow_empty:
                return {}
            else:
                raise ValidationError(
                    "JSON cannot be empty",
                    variable_name=context.variable_name if context else None,
                    suggestion="Provide valid JSON content"
                )
        
        # Parse JSON
        try:
            parsed_json = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON format: {str(e)}",
                variable_name=context.variable_name if context else None,
                suggestion="Check JSON syntax and ensure all brackets are properly closed"
            )
        
        # Validate against schema if provided
        if self.schema:
            try:
                from jsonschema import validate, ValidationError as SchemaError
                validate(instance=parsed_json, schema=self.schema)
            except ImportError:
                self.logger.warning("jsonschema library not available, skipping schema validation")
            except SchemaError as e:
                raise ValidationError(
                    f"JSON does not match schema: {str(e)}",
                    variable_name=context.variable_name if context else None,
                    suggestion="Check that JSON structure matches the required schema"
                )
        
        return parsed_json


@validator("file_path")
class FilePathValidator(BaseValidator):
    """
    Validator for file paths with existence and permission checking.
    
    This validator ensures that file paths are valid and optionally
    checks if files exist and are accessible.
    """
    
    def __init__(
        self,
        check_exists: bool = False,
        check_readable: bool = False,
        check_writable: bool = False,
        allowed_extensions: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize the file path validator.
        
        Args:
            check_exists: Whether to check if file exists
            check_readable: Whether to check if file is readable
            check_writable: Whether to check if file is writable
            allowed_extensions: List of allowed file extensions
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.check_exists = check_exists
        self.check_readable = check_readable
        self.check_writable = check_writable
        self.allowed_extensions = allowed_extensions
        
        self.examples = [
            "/path/to/file.txt",
            "config/settings.json",
            "data/input.csv",
            "logs/app.log"
        ]
        self.suggestions = [
            "Use absolute or relative file paths",
            "Check that the file path is correct",
            "Ensure the file has the required permissions",
            "Use forward slashes for cross-platform compatibility"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate a file path.
        
        Args:
            value: The file path to validate
            context: Optional validation context
            
        Returns:
            The validated file path
            
        Raises:
            ValidationError: If the file path doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"File path must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Normalize path
        try:
            path = Path(value).resolve()
        except Exception as e:
            raise ValidationError(
                f"Invalid file path: {str(e)}",
                variable_name=context.variable_name if context else None,
                suggestion="Check path format and ensure it's valid for your operating system"
            )
        
        # Check file extension if specified
        if self.allowed_extensions:
            file_extension = path.suffix.lower()
            if file_extension not in self.allowed_extensions:
                raise ValidationError(
                    f"File extension '{file_extension}' not allowed. Allowed extensions: {', '.join(self.allowed_extensions)}",
                    variable_name=context.variable_name if context else None,
                    suggestion=f"Use one of the allowed file extensions: {', '.join(self.allowed_extensions)}"
                )
        
        # Check if file exists
        if self.check_exists and not path.exists():
            raise ValidationError(
                f"File does not exist: {path}",
                variable_name=context.variable_name if context else None,
                suggestion="Check that the file exists and the path is correct"
            )
        
        # Check file permissions
        if path.exists():
            if self.check_readable and not os.access(path, os.R_OK):
                raise ValidationError(
                    f"File is not readable: {path}",
                    variable_name=context.variable_name if context else None,
                    suggestion="Check file permissions or run with appropriate privileges"
                )
            
            if self.check_writable and not os.access(path, os.W_OK):
                raise ValidationError(
                    f"File is not writable: {path}",
                    variable_name=context.variable_name if context else None,
                    suggestion="Check file permissions or run with appropriate privileges"
                )
        
        return str(path)


@validator("directory_path")
class DirectoryPathValidator(BaseValidator):
    """
    Validator for directory paths with existence and permission checking.
    
    This validator ensures that directory paths are valid and optionally
    checks if directories exist and are accessible.
    """
    
    def __init__(
        self,
        check_exists: bool = False,
        check_readable: bool = False,
        check_writable: bool = False,
        create_if_missing: bool = False,
        **kwargs
    ):
        """
        Initialize the directory path validator.
        
        Args:
            check_exists: Whether to check if directory exists
            check_readable: Whether to check if directory is readable
            check_writable: Whether to check if directory is writable
            create_if_missing: Whether to create directory if it doesn't exist
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.check_exists = check_exists
        self.check_readable = check_readable
        self.check_writable = check_writable
        self.create_if_missing = create_if_missing
        
        self.examples = [
            "/path/to/directory",
            "config/",
            "data/input/",
            "logs/"
        ]
        self.suggestions = [
            "Use absolute or relative directory paths",
            "Check that the directory path is correct",
            "Ensure the directory has the required permissions",
            "Use forward slashes for cross-platform compatibility"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate a directory path.
        
        Args:
            value: The directory path to validate
            context: Optional validation context
            
        Returns:
            The validated directory path
            
        Raises:
            ValidationError: If the directory path doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Directory path must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Normalize path
        try:
            path = Path(value).resolve()
        except Exception as e:
            raise ValidationError(
                f"Invalid directory path: {str(e)}",
                variable_name=context.variable_name if context else None,
                suggestion="Check path format and ensure it's valid for your operating system"
            )
        
        # Check if directory exists
        if not path.exists():
            if self.create_if_missing:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created directory: {path}")
                except Exception as e:
                    raise ValidationError(
                        f"Failed to create directory: {str(e)}",
                        variable_name=context.variable_name if context else None,
                        suggestion="Check permissions and ensure parent directories exist"
                    )
            elif self.check_exists:
                raise ValidationError(
                    f"Directory does not exist: {path}",
                    variable_name=context.variable_name if context else None,
                    suggestion="Check that the directory exists and the path is correct"
                )
        
        # Check if it's actually a directory
        if path.exists() and not path.is_dir():
            raise ValidationError(
                f"Path exists but is not a directory: {path}",
                variable_name=context.variable_name if context else None,
                suggestion="Ensure the path points to a directory, not a file"
            )
        
        # Check directory permissions
        if path.exists():
            if self.check_readable and not os.access(path, os.R_OK):
                raise ValidationError(
                    f"Directory is not readable: {path}",
                    variable_name=context.variable_name if context else None,
                    suggestion="Check directory permissions or run with appropriate privileges"
                )
            
            if self.check_writable and not os.access(path, os.W_OK):
                raise ValidationError(
                    f"Directory is not writable: {path}",
                    variable_name=context.variable_name if context else None,
                    suggestion="Check directory permissions or run with appropriate privileges"
                )
        
        return str(path) 