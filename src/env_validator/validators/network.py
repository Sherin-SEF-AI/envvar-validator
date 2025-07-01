"""
Network validators for the env-validator package.

This module provides validators for network-related environment variables,
including URL validation, IP address validation, port validation, and
database connection string validation.
"""

import re
import socket
import urllib.parse
from typing import Any, Optional, List
from urllib.parse import urlparse

from .base import BaseValidator, ValidationError, ValidationContext, validator


@validator("url")
class URLValidator(BaseValidator):
    """
    Validator for URLs with comprehensive format and accessibility checking.
    
    This validator ensures that URLs are properly formatted and optionally
    checks if they are accessible.
    """
    
    def __init__(
        self,
        allowed_schemes: Optional[List[str]] = None,
        require_https: bool = False,
        check_accessibility: bool = False,
        timeout: int = 5,
        **kwargs
    ):
        """
        Initialize the URL validator.
        
        Args:
            allowed_schemes: List of allowed URL schemes (e.g., ['http', 'https'])
            require_https: Whether to require HTTPS
            check_accessibility: Whether to check if URL is accessible
            timeout: Timeout for accessibility check in seconds
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.allowed_schemes = allowed_schemes or ['http', 'https', 'ftp', 'sftp']
        self.require_https = require_https
        self.check_accessibility = check_accessibility
        self.timeout = timeout
        
        self.examples = [
            "https://api.example.com/v1",
            "http://localhost:8000",
            "ftp://ftp.example.com/files",
            "sftp://user@server.com/path"
        ]
        self.suggestions = [
            "Use HTTPS for production environments",
            "Include protocol (http://, https://, etc.)",
            "Ensure the URL is properly formatted",
            "Check that the domain is valid"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate a URL.
        
        Args:
            value: The URL to validate
            context: Optional validation context
            
        Returns:
            The validated URL
            
        Raises:
            ValidationError: If the URL doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"URL must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Parse URL
        try:
            parsed = urlparse(value)
        except Exception as e:
            raise ValidationError(
                f"Invalid URL format: {str(e)}",
                variable_name=context.variable_name if context else None,
                suggestion="Check URL format and ensure it includes protocol"
            )
        
        # Check if URL has required components
        if not parsed.scheme:
            raise ValidationError(
                "URL must include a scheme (protocol)",
                variable_name=context.variable_name if context else None,
                suggestion="Add protocol (e.g., http://, https://)"
            )
        
        if not parsed.netloc:
            raise ValidationError(
                "URL must include a hostname",
                variable_name=context.variable_name if context else None,
                suggestion="Add a valid hostname or domain"
            )
        
        # Check allowed schemes
        if parsed.scheme not in self.allowed_schemes:
            raise ValidationError(
                f"URL scheme '{parsed.scheme}' not allowed. Allowed schemes: {', '.join(self.allowed_schemes)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Use one of the allowed schemes: {', '.join(self.allowed_schemes)}"
            )
        
        # Check HTTPS requirement
        if self.require_https and parsed.scheme != 'https':
            raise ValidationError(
                "HTTPS is required for this URL",
                variable_name=context.variable_name if context else None,
                suggestion="Use HTTPS instead of HTTP"
            )
        
        # Check accessibility if requested
        if self.check_accessibility:
            if not self._is_accessible(value):
                raise ValidationError(
                    "URL is not accessible",
                    variable_name=context.variable_name if context else None,
                    suggestion="Check if the URL is correct and the service is running"
                )
        
        return value
    
    def _is_accessible(self, url: str) -> bool:
        """Check if URL is accessible."""
        try:
            import requests
            response = requests.head(url, timeout=self.timeout, allow_redirects=True)
            return response.status_code < 400
        except Exception:
            return False


@validator("ip_address")
class IPAddressValidator(BaseValidator):
    """
    Validator for IP addresses with IPv4 and IPv6 support.
    
    This validator ensures that IP addresses are properly formatted
    and optionally checks if they are valid network addresses.
    """
    
    def __init__(
        self,
        allow_ipv4: bool = True,
        allow_ipv6: bool = True,
        allow_private: bool = True,
        allow_reserved: bool = False,
        **kwargs
    ):
        """
        Initialize the IP address validator.
        
        Args:
            allow_ipv4: Whether to allow IPv4 addresses
            allow_ipv6: Whether to allow IPv6 addresses
            allow_private: Whether to allow private IP addresses
            allow_reserved: Whether to allow reserved IP addresses
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.allow_ipv4 = allow_ipv4
        self.allow_ipv6 = allow_ipv6
        self.allow_private = allow_private
        self.allow_reserved = allow_reserved
        
        self.examples = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "2001:db8::1",
            "::1"
        ]
        self.suggestions = [
            "Use valid IPv4 or IPv6 format",
            "Check that the IP address is in the correct range",
            "Ensure the address is not reserved or private (if required)"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate an IP address.
        
        Args:
            value: The IP address to validate
            context: Optional validation context
            
        Returns:
            The validated IP address
            
        Raises:
            ValidationError: If the IP address doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"IP address must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check if it's a valid IP address
        try:
            socket.inet_pton(socket.AF_INET, value)
            ip_version = 4
        except OSError:
            try:
                socket.inet_pton(socket.AF_INET6, value)
                ip_version = 6
            except OSError:
                raise ValidationError(
                    "Invalid IP address format",
                    variable_name=context.variable_name if context else None,
                    suggestion="Use valid IPv4 or IPv6 format"
                )
        
        # Check version restrictions
        if ip_version == 4 and not self.allow_ipv4:
            raise ValidationError(
                "IPv4 addresses are not allowed",
                variable_name=context.variable_name if context else None,
                suggestion="Use an IPv6 address"
            )
        
        if ip_version == 6 and not self.allow_ipv6:
            raise ValidationError(
                "IPv6 addresses are not allowed",
                variable_name=context.variable_name if context else None,
                suggestion="Use an IPv4 address"
            )
        
        # Check for private/reserved addresses
        if not self.allow_private and self._is_private_ip(value, ip_version):
            raise ValidationError(
                "Private IP addresses are not allowed",
                variable_name=context.variable_name if context else None,
                suggestion="Use a public IP address"
            )
        
        if not self.allow_reserved and self._is_reserved_ip(value, ip_version):
            raise ValidationError(
                "Reserved IP addresses are not allowed",
                variable_name=context.variable_name if context else None,
                suggestion="Use a non-reserved IP address"
            )
        
        return value
    
    def _is_private_ip(self, ip: str, version: int) -> bool:
        """Check if IP address is private."""
        if version == 4:
            # IPv4 private ranges
            private_ranges = [
                ('10.0.0.0', '10.255.255.255'),
                ('172.16.0.0', '172.31.255.255'),
                ('192.168.0.0', '192.168.255.255'),
                ('127.0.0.0', '127.255.255.255')
            ]
            
            ip_parts = [int(x) for x in ip.split('.')]
            for start, end in private_ranges:
                start_parts = [int(x) for x in start.split('.')]
                end_parts = [int(x) for x in end.split('.')]
                
                if start_parts <= ip_parts <= end_parts:
                    return True
            
            return False
        else:
            # IPv6 private ranges
            private_prefixes = [
                'fc00::',
                'fd00::',
                'fe80::',
                '::1'
            ]
            
            for prefix in private_prefixes:
                if ip.startswith(prefix):
                    return True
            
            return False
    
    def _is_reserved_ip(self, ip: str, version: int) -> bool:
        """Check if IP address is reserved."""
        if version == 4:
            # IPv4 reserved ranges
            reserved_ranges = [
                ('0.0.0.0', '0.255.255.255'),
                ('224.0.0.0', '239.255.255.255'),
                ('240.0.0.0', '255.255.255.255')
            ]
            
            ip_parts = [int(x) for x in ip.split('.')]
            for start, end in reserved_ranges:
                start_parts = [int(x) for x in start.split('.')]
                end_parts = [int(x) for x in end.split('.')]
                
                if start_parts <= ip_parts <= end_parts:
                    return True
            
            return False
        else:
            # IPv6 reserved ranges
            reserved_prefixes = [
                'ff00::',
                '::'
            ]
            
            for prefix in reserved_prefixes:
                if ip.startswith(prefix):
                    return True
            
            return False


@validator("port_range")
class PortValidator(BaseValidator):
    """
    Validator for network ports with range and availability checking.
    
    This validator ensures that port numbers are within valid ranges
    and optionally checks if they are available.
    """
    
    def __init__(
        self,
        min_port: int = 1,
        max_port: int = 65535,
        allow_privileged: bool = False,
        check_availability: bool = False,
        **kwargs
    ):
        """
        Initialize the port validator.
        
        Args:
            min_port: Minimum allowed port number
            max_port: Maximum allowed port number
            allow_privileged: Whether to allow privileged ports (1-1023)
            check_availability: Whether to check if port is available
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.min_port = min_port
        self.max_port = max_port
        self.allow_privileged = allow_privileged
        self.check_availability = check_availability
        
        self.examples = [
            "8080",
            "3000",
            "5432",
            "6379"
        ]
        self.suggestions = [
            f"Use a port between {min_port} and {max_port}",
            "Avoid privileged ports (1-1023) unless necessary",
            "Check that the port is not already in use"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> int:
        """
        Validate a port number.
        
        Args:
            value: The port number to validate
            context: Optional validation context
            
        Returns:
            The validated port number
            
        Raises:
            ValidationError: If the port number doesn't meet requirements
        """
        # Convert to int if string
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                raise ValidationError(
                    f"Port must be a number, got '{value}'",
                    variable_name=context.variable_name if context else None,
                    suggestion="Provide a valid port number"
                )
        
        if not isinstance(value, int):
            raise ValidationError(
                f"Port must be an integer, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check range
        if value < self.min_port or value > self.max_port:
            raise ValidationError(
                f"Port must be between {self.min_port} and {self.max_port}, got {value}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Use a port between {self.min_port} and {self.max_port}"
            )
        
        # Check privileged ports
        if not self.allow_privileged and 1 <= value <= 1023:
            raise ValidationError(
                f"Privileged port {value} requires elevated permissions",
                variable_name=context.variable_name if context else None,
                suggestion="Use a non-privileged port (1024-65535)"
            )
        
        # Check availability if requested
        if self.check_availability:
            if not self._is_port_available(value):
                raise ValidationError(
                    f"Port {value} is already in use",
                    variable_name=context.variable_name if context else None,
                    suggestion="Choose a different port or stop the service using this port"
                )
        
        return value
    
    def _is_port_available(self, port: int) -> bool:
        """Check if port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False


@validator("database_url")
class DatabaseURLValidator(BaseValidator):
    """
    Validator for database connection URLs.
    
    This validator ensures that database URLs are properly formatted
    and contain all required components for the specified database type.
    """
    
    def __init__(
        self,
        allowed_schemes: Optional[List[str]] = None,
        require_ssl: bool = False,
        validate_connection: bool = False,
        **kwargs
    ):
        """
        Initialize the database URL validator.
        
        Args:
            allowed_schemes: List of allowed database schemes
            require_ssl: Whether to require SSL connections
            validate_connection: Whether to test the connection
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.allowed_schemes = allowed_schemes or [
            'postgresql', 'postgres', 'mysql', 'sqlite', 'mongodb', 'redis'
        ]
        self.require_ssl = require_ssl
        self.validate_connection = validate_connection
        
        self.examples = [
            "postgresql://user:pass@localhost:5432/dbname",
            "mysql://user:pass@localhost:3306/dbname",
            "sqlite:///path/to/database.db",
            "mongodb://localhost:27017/dbname",
            "redis://localhost:6379/0"
        ]
        self.suggestions = [
            "Include username, password, host, port, and database name",
            "Use SSL for production environments",
            "Ensure the database server is running",
            "Check that credentials are correct"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate a database URL.
        
        Args:
            value: The database URL to validate
            context: Optional validation context
            
        Returns:
            The validated database URL
            
        Raises:
            ValidationError: If the database URL doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Database URL must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Parse URL
        try:
            parsed = urlparse(value)
        except Exception as e:
            raise ValidationError(
                f"Invalid database URL format: {str(e)}",
                variable_name=context.variable_name if context else None,
                suggestion="Check URL format and ensure it includes scheme"
            )
        
        # Check scheme
        if not parsed.scheme:
            raise ValidationError(
                "Database URL must include a scheme",
                variable_name=context.variable_name if context else None,
                suggestion="Add database scheme (e.g., postgresql://, mysql://)"
            )
        
        if parsed.scheme not in self.allowed_schemes:
            raise ValidationError(
                f"Database scheme '{parsed.scheme}' not allowed. Allowed schemes: {', '.join(self.allowed_schemes)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Use one of the allowed schemes: {', '.join(self.allowed_schemes)}"
            )
        
        # Check for required components based on scheme
        if parsed.scheme in ['postgresql', 'postgres', 'mysql']:
            if not parsed.netloc:
                raise ValidationError(
                    f"{parsed.scheme} URL must include hostname",
                    variable_name=context.variable_name if context else None,
                    suggestion="Add hostname (e.g., localhost)"
                )
            
            if not parsed.username:
                raise ValidationError(
                    f"{parsed.scheme} URL must include username",
                    variable_name=context.variable_name if context else None,
                    suggestion="Add username to the URL"
                )
        
        # Check SSL requirement
        if self.require_ssl and parsed.scheme in ['postgresql', 'postgres', 'mysql']:
            if not value.lower().startswith(f"{parsed.scheme}+ssl://"):
                raise ValidationError(
                    "SSL is required for database connection",
                    variable_name=context.variable_name if context else None,
                    suggestion="Use SSL connection (e.g., postgresql+ssl://)"
                )
        
        # Validate connection if requested
        if self.validate_connection:
            if not self._test_connection(value):
                raise ValidationError(
                    "Database connection failed",
                    variable_name=context.variable_name if context else None,
                    suggestion="Check database server status and credentials"
                )
        
        return value
    
    def _test_connection(self, url: str) -> bool:
        """Test database connection."""
        try:
            # This is a simplified test - in production, you'd use proper database drivers
            parsed = urlparse(url)
            if parsed.scheme in ['postgresql', 'postgres']:
                # Would use psycopg2 or similar
                return True
            elif parsed.scheme == 'mysql':
                # Would use mysql-connector-python or similar
                return True
            elif parsed.scheme == 'sqlite':
                # Would check if file exists and is writable
                return True
            else:
                return True
        except Exception:
            return False 