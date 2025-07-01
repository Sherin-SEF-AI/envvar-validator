"""
Security validators for the env-validator package.

This module provides validators focused on security aspects of environment
variables, including secret key validation, API key validation, encryption
key validation, and password strength checking.
"""

import re
import secrets
import hashlib
from typing import Any, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .base import BaseValidator, ValidationError, ValidationContext, validator


@validator("secret_key")
class SecretKeyValidator(BaseValidator):
    """
    Validator for secret keys with entropy and strength checking.
    
    This validator ensures that secret keys meet security requirements
    including minimum length, entropy, and character diversity.
    """
    
    def __init__(self, min_length: int = 32, min_entropy: float = 3.0, **kwargs):
        """
        Initialize the secret key validator.
        
        Args:
            min_length: Minimum length for the secret key
            min_entropy: Minimum entropy score (0-4 scale)
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.min_length = min_length
        self.min_entropy = min_entropy
        self.examples = [
            "your-super-secret-key-here-make-it-long-and-random",
            secrets.token_urlsafe(32),
            secrets.token_hex(32)
        ]
        self.suggestions = [
            f"Use at least {min_length} characters",
            "Include a mix of uppercase, lowercase, numbers, and symbols",
            "Use a cryptographically secure random generator",
            "Avoid predictable patterns or common words"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate a secret key.
        
        Args:
            value: The secret key to validate
            context: Optional validation context
            
        Returns:
            The validated secret key
            
        Raises:
            ValidationError: If the secret key doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Secret key must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check minimum length
        if len(value) < self.min_length:
            raise ValidationError(
                f"Secret key must be at least {self.min_length} characters long, got {len(value)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Increase the length to at least {self.min_length} characters"
            )
        
        # Calculate entropy
        entropy = self._calculate_entropy(value)
        if entropy < self.min_entropy:
            raise ValidationError(
                f"Secret key entropy too low: {entropy:.2f} (minimum: {self.min_entropy})",
                variable_name=context.variable_name if context else None,
                suggestion="Use more diverse characters and avoid patterns"
            )
        
        # Check for common weak patterns
        if self._has_weak_patterns(value):
            raise ValidationError(
                "Secret key contains weak patterns",
                variable_name=context.variable_name if context else None,
                suggestion="Avoid common words, sequences, or predictable patterns"
            )
        
        return value
    
    def _calculate_entropy(self, value: str) -> float:
        """Calculate the entropy of a string."""
        if not value:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in value:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        length = len(value)
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def _has_weak_patterns(self, value: str) -> bool:
        """Check for weak patterns in the secret key."""
        # Common weak patterns
        weak_patterns = [
            r'password',
            r'secret',
            r'key',
            r'123',
            r'abc',
            r'qwerty',
            r'admin',
            r'root',
            r'test',
            r'demo',
        ]
        
        value_lower = value.lower()
        for pattern in weak_patterns:
            if re.search(pattern, value_lower):
                return True
        
        # Check for repeated characters
        if re.search(r'(.)\1{3,}', value):
            return True
        
        # Check for sequential characters
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', value_lower):
            return True
        
        return False


@validator("api_key")
class APIKeyValidator(BaseValidator):
    """
    Validator for API keys with format and security checking.
    
    This validator ensures that API keys meet common format requirements
    and security standards.
    """
    
    def __init__(self, min_length: int = 16, require_prefix: bool = False, **kwargs):
        """
        Initialize the API key validator.
        
        Args:
            min_length: Minimum length for the API key
            require_prefix: Whether to require a prefix (e.g., 'api_')
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.min_length = min_length
        self.require_prefix = require_prefix
        self.examples = [
            "api_1234567890abcdef1234567890abcdef",
            "sk_live_1234567890abcdef1234567890abcdef",
            "pk_test_1234567890abcdef1234567890abcdef"
        ]
        self.suggestions = [
            f"Use at least {min_length} characters",
            "Include a prefix to identify the key type",
            "Use alphanumeric characters and hyphens/underscores",
            "Store securely and never commit to version control"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate an API key.
        
        Args:
            value: The API key to validate
            context: Optional validation context
            
        Returns:
            The validated API key
            
        Raises:
            ValidationError: If the API key doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"API key must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check minimum length
        if len(value) < self.min_length:
            raise ValidationError(
                f"API key must be at least {self.min_length} characters long, got {len(value)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Increase the length to at least {self.min_length} characters"
            )
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValidationError(
                "API key contains invalid characters",
                variable_name=context.variable_name if context else None,
                suggestion="Use only alphanumeric characters, hyphens, and underscores"
            )
        
        # Check prefix if required
        if self.require_prefix and not re.match(r'^[a-zA-Z_]+_', value):
            raise ValidationError(
                "API key must have a prefix (e.g., 'api_', 'sk_', 'pk_')",
                variable_name=context.variable_name if context else None,
                suggestion="Add a descriptive prefix to identify the key type"
            )
        
        return value


@validator("encryption_key")
class EncryptionKeyValidator(BaseValidator):
    """
    Validator for encryption keys with cryptographic strength checking.
    
    This validator ensures that encryption keys meet cryptographic
    requirements for security and compatibility.
    """
    
    def __init__(self, key_size: int = 256, encoding: str = 'base64', **kwargs):
        """
        Initialize the encryption key validator.
        
        Args:
            key_size: Required key size in bits (128, 192, 256)
            encoding: Expected encoding ('base64', 'hex', 'raw')
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.key_size = key_size
        self.encoding = encoding
        self.examples = [
            "your-32-byte-encryption-key-here",
            secrets.token_urlsafe(32),
            secrets.token_hex(32)
        ]
        self.suggestions = [
            f"Use a {key_size}-bit key ({key_size // 8} bytes)",
            "Generate using a cryptographically secure random generator",
            "Store securely and never expose in logs or error messages",
            "Use appropriate encoding for your application"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate an encryption key.
        
        Args:
            value: The encryption key to validate
            context: Optional validation context
            
        Returns:
            The validated encryption key
            
        Raises:
            ValidationError: If the encryption key doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Encryption key must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check encoding and decode to get actual key size
        try:
            if self.encoding == 'base64':
                import base64
                key_bytes = base64.b64decode(value)
            elif self.encoding == 'hex':
                key_bytes = bytes.fromhex(value)
            elif self.encoding == 'raw':
                key_bytes = value.encode('utf-8')
            else:
                raise ValidationError(
                    f"Unsupported encoding: {self.encoding}",
                    variable_name=context.variable_name if context else None
                )
        except Exception as e:
            raise ValidationError(
                f"Failed to decode encryption key: {str(e)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Ensure the key is properly encoded in {self.encoding} format"
            )
        
        # Check key size
        expected_bytes = self.key_size // 8
        if len(key_bytes) != expected_bytes:
            raise ValidationError(
                f"Encryption key must be {expected_bytes} bytes ({self.key_size} bits), got {len(key_bytes)} bytes",
                variable_name=context.variable_name if context else None,
                suggestion=f"Generate a {self.key_size}-bit key"
            )
        
        return value


@validator("password_strength")
class PasswordStrengthValidator(BaseValidator):
    """
    Validator for password strength with comprehensive checking.
    
    This validator ensures that passwords meet strength requirements
    including complexity, length, and common password checking.
    """
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_symbols: bool = True,
        max_common_passwords: int = 1000,
        **kwargs
    ):
        """
        Initialize the password strength validator.
        
        Args:
            min_length: Minimum password length
            require_uppercase: Whether to require uppercase letters
            require_lowercase: Whether to require lowercase letters
            require_digits: Whether to require digits
            require_symbols: Whether to require symbols
            max_common_passwords: Maximum rank in common passwords list
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_symbols = require_symbols
        self.max_common_passwords = max_common_passwords
        
        self.examples = [
            "MySecureP@ssw0rd123!",
            "Complex#Password$2024",
            "Str0ng!P@ssw0rd#Here"
        ]
        self.suggestions = [
            f"Use at least {min_length} characters",
            "Include uppercase and lowercase letters" if require_uppercase and require_lowercase else "",
            "Include numbers" if require_digits else "",
            "Include special characters" if require_symbols else "",
            "Avoid common passwords and patterns",
            "Don't use personal information"
        ]
        # Remove empty suggestions
        self.suggestions = [s for s in self.suggestions if s]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate password strength.
        
        Args:
            value: The password to validate
            context: Optional validation context
            
        Returns:
            The validated password
            
        Raises:
            ValidationError: If the password doesn't meet strength requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Password must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check minimum length
        if len(value) < self.min_length:
            raise ValidationError(
                f"Password must be at least {self.min_length} characters long, got {len(value)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Increase the length to at least {self.min_length} characters"
            )
        
        # Check character requirements
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            raise ValidationError(
                "Password must contain at least one uppercase letter",
                variable_name=context.variable_name if context else None,
                suggestion="Add at least one uppercase letter (A-Z)"
            )
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            raise ValidationError(
                "Password must contain at least one lowercase letter",
                variable_name=context.variable_name if context else None,
                suggestion="Add at least one lowercase letter (a-z)"
            )
        
        if self.require_digits and not re.search(r'\d', value):
            raise ValidationError(
                "Password must contain at least one digit",
                variable_name=context.variable_name if context else None,
                suggestion="Add at least one digit (0-9)"
            )
        
        if self.require_symbols and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', value):
            raise ValidationError(
                "Password must contain at least one special character",
                variable_name=context.variable_name if context else None,
                suggestion="Add at least one special character (!@#$%^&*...)"
            )
        
        # Check for common patterns
        if self._is_common_password(value):
            raise ValidationError(
                "Password is too common",
                variable_name=context.variable_name if context else None,
                suggestion="Choose a more unique password"
            )
        
        return value
    
    def _is_common_password(self, password: str) -> bool:
        """Check if password is in common passwords list."""
        # This is a simplified check - in production, you'd use a comprehensive list
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        
        return password.lower() in common_passwords 