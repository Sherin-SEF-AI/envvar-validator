"""
Cloud validators for the env-validator package.

This module provides validators for cloud platform identifiers,
including AWS ARNs, GCP project IDs, and Azure resource identifiers.
"""

import re
from typing import Any, Optional, List

from .base import BaseValidator, ValidationError, ValidationContext, validator


@validator("aws_arn")
class AWSARNValidator(BaseValidator):
    """
    Validator for AWS ARNs (Amazon Resource Names).
    
    This validator ensures that AWS ARNs are properly formatted
    according to AWS standards.
    """
    
    def __init__(
        self,
        allowed_services: Optional[List[str]] = None,
        allowed_regions: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize the AWS ARN validator.
        
        Args:
            allowed_services: List of allowed AWS services
            allowed_regions: List of allowed AWS regions
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.allowed_services = allowed_services
        self.allowed_regions = allowed_regions
        
        self.examples = [
            "arn:aws:s3:::my-bucket",
            "arn:aws:iam::123456789012:user/username",
            "arn:aws:lambda:us-east-1:123456789012:function:my-function",
            "arn:aws:ec2:us-west-2:123456789012:instance/i-1234567890abcdef0"
        ]
        self.suggestions = [
            "Use the format: arn:aws:service:region:account:resource",
            "Ensure the AWS account ID is 12 digits",
            "Check that the service name is valid",
            "Verify the region is correct for your AWS account"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate an AWS ARN.
        
        Args:
            value: The AWS ARN to validate
            context: Optional validation context
            
        Returns:
            The validated AWS ARN
            
        Raises:
            ValidationError: If the AWS ARN doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"AWS ARN must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # AWS ARN pattern
        arn_pattern = r'^arn:aws:([^:]+):([^:]*):(\d{12}):(.+)$'
        match = re.match(arn_pattern, value)
        
        if not match:
            raise ValidationError(
                "Invalid AWS ARN format",
                variable_name=context.variable_name if context else None,
                suggestion="Use format: arn:aws:service:region:account:resource"
            )
        
        service, region, account_id, resource = match.groups()
        
        # Validate service
        if self.allowed_services and service not in self.allowed_services:
            raise ValidationError(
                f"AWS service '{service}' not allowed. Allowed services: {', '.join(self.allowed_services)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Use one of the allowed services: {', '.join(self.allowed_services)}"
            )
        
        # Validate region
        if self.allowed_regions and region and region not in self.allowed_regions:
            raise ValidationError(
                f"AWS region '{region}' not allowed. Allowed regions: {', '.join(self.allowed_regions)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Use one of the allowed regions: {', '.join(self.allowed_regions)}"
            )
        
        # Validate account ID
        if not re.match(r'^\d{12}$', account_id):
            raise ValidationError(
                f"Invalid AWS account ID: {account_id}",
                variable_name=context.variable_name if context else None,
                suggestion="AWS account ID must be exactly 12 digits"
            )
        
        return value


@validator("gcp_project_id")
class GCPProjectIDValidator(BaseValidator):
    """
    Validator for Google Cloud Platform project IDs.
    
    This validator ensures that GCP project IDs are properly formatted
    according to Google Cloud standards.
    """
    
    def __init__(
        self,
        allow_numeric: bool = True,
        **kwargs
    ):
        """
        Initialize the GCP project ID validator.
        
        Args:
            allow_numeric: Whether to allow numeric project IDs
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.allow_numeric = allow_numeric
        
        self.examples = [
            "my-project-123",
            "project-name",
            "my-project-name-2024",
            "123456789012"  # if allow_numeric is True
        ]
        self.suggestions = [
            "Use lowercase letters, numbers, and hyphens only",
            "Start with a letter (unless numeric project ID)",
            "End with a letter or number",
            "Keep between 6 and 30 characters"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate a GCP project ID.
        
        Args:
            value: The GCP project ID to validate
            context: Optional validation context
            
        Returns:
            The validated GCP project ID
            
        Raises:
            ValidationError: If the GCP project ID doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"GCP project ID must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check length
        if len(value) < 6 or len(value) > 30:
            raise ValidationError(
                f"GCP project ID must be between 6 and 30 characters, got {len(value)}",
                variable_name=context.variable_name if context else None,
                suggestion="Adjust the length to be between 6 and 30 characters"
            )
        
        # Check for numeric project ID
        if value.isdigit():
            if not self.allow_numeric:
                raise ValidationError(
                    "Numeric project IDs are not allowed",
                    variable_name=context.variable_name if context else None,
                    suggestion="Use a project ID with letters and hyphens"
                )
            return value
        
        # Check format for non-numeric project IDs
        if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', value):
            raise ValidationError(
                "Invalid GCP project ID format",
                variable_name=context.variable_name if context else None,
                suggestion="Use lowercase letters, numbers, and hyphens. Start with a letter and end with a letter or number"
            )
        
        # Check for consecutive hyphens
        if '--' in value:
            raise ValidationError(
                "GCP project ID cannot contain consecutive hyphens",
                variable_name=context.variable_name if context else None,
                suggestion="Remove consecutive hyphens"
            )
        
        return value


@validator("azure_resource_id")
class AzureResourceIDValidator(BaseValidator):
    """
    Validator for Azure resource identifiers.
    
    This validator ensures that Azure resource IDs are properly formatted
    according to Azure standards.
    """
    
    def __init__(
        self,
        allowed_subscriptions: Optional[List[str]] = None,
        allowed_resource_groups: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize the Azure resource ID validator.
        
        Args:
            allowed_subscriptions: List of allowed subscription IDs
            allowed_resource_groups: List of allowed resource group names
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.allowed_subscriptions = allowed_subscriptions
        self.allowed_resource_groups = allowed_resource_groups
        
        self.examples = [
            "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myResourceGroup/providers/Microsoft.Storage/storageAccounts/mystorageaccount",
            "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVM",
            "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myResourceGroup/providers/Microsoft.Web/sites/myWebApp"
        ]
        self.suggestions = [
            "Use the format: /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/{provider}/{resource-type}/{resource-name}",
            "Ensure the subscription ID is a valid GUID",
            "Check that the resource group name is valid",
            "Verify the provider and resource type are correct"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate an Azure resource ID.
        
        Args:
            value: The Azure resource ID to validate
            context: Optional validation context
            
        Returns:
            The validated Azure resource ID
            
        Raises:
            ValidationError: If the Azure resource ID doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Azure resource ID must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Azure resource ID pattern
        resource_id_pattern = r'^/subscriptions/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/resourceGroups/([^/]+)/providers/([^/]+)/([^/]+)/(.+)$'
        match = re.match(resource_id_pattern, value)
        
        if not match:
            raise ValidationError(
                "Invalid Azure resource ID format",
                variable_name=context.variable_name if context else None,
                suggestion="Use format: /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/{provider}/{resource-type}/{resource-name}"
            )
        
        subscription_id, resource_group, provider, resource_type, resource_name = match.groups()
        
        # Validate subscription ID
        if self.allowed_subscriptions and subscription_id not in self.allowed_subscriptions:
            raise ValidationError(
                f"Azure subscription '{subscription_id}' not allowed. Allowed subscriptions: {', '.join(self.allowed_subscriptions)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Use one of the allowed subscriptions: {', '.join(self.allowed_subscriptions)}"
            )
        
        # Validate resource group
        if self.allowed_resource_groups and resource_group not in self.allowed_resource_groups:
            raise ValidationError(
                f"Azure resource group '{resource_group}' not allowed. Allowed resource groups: {', '.join(self.allowed_resource_groups)}",
                variable_name=context.variable_name if context else None,
                suggestion=f"Use one of the allowed resource groups: {', '.join(self.allowed_resource_groups)}"
            )
        
        # Validate resource group name format
        if not re.match(r'^[a-zA-Z0-9._()-]+$', resource_group):
            raise ValidationError(
                f"Invalid Azure resource group name: {resource_group}",
                variable_name=context.variable_name if context else None,
                suggestion="Resource group names can contain letters, numbers, periods, underscores, hyphens, and parentheses"
            )
        
        # Validate provider format
        if not re.match(r'^[A-Za-z0-9.]+$', provider):
            raise ValidationError(
                f"Invalid Azure provider name: {provider}",
                variable_name=context.variable_name if context else None,
                suggestion="Provider names can contain letters, numbers, and periods"
            )
        
        return value


@validator("kubernetes_secret")
class KubernetesSecretValidator(BaseValidator):
    """
    Validator for Kubernetes secret names.
    
    This validator ensures that Kubernetes secret names are properly formatted
    according to Kubernetes naming conventions.
    """
    
    def __init__(
        self,
        allow_namespace_prefix: bool = True,
        **kwargs
    ):
        """
        Initialize the Kubernetes secret validator.
        
        Args:
            allow_namespace_prefix: Whether to allow namespace prefixes
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.allow_namespace_prefix = allow_namespace_prefix
        
        self.examples = [
            "my-secret",
            "app-config-secret",
            "database-credentials",
            "default/my-secret"  # if allow_namespace_prefix is True
        ]
        self.suggestions = [
            "Use lowercase letters, numbers, hyphens, and dots only",
            "Start and end with a letter or number",
            "Keep between 1 and 253 characters",
            "Use descriptive names for better organization"
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> str:
        """
        Validate a Kubernetes secret name.
        
        Args:
            value: The Kubernetes secret name to validate
            context: Optional validation context
            
        Returns:
            The validated Kubernetes secret name
            
        Raises:
            ValidationError: If the Kubernetes secret name doesn't meet requirements
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Kubernetes secret name must be a string, got {type(value).__name__}",
                variable_name=context.variable_name if context else None
            )
        
        # Check for namespace prefix
        if '/' in value:
            if not self.allow_namespace_prefix:
                raise ValidationError(
                    "Namespace prefixes are not allowed",
                    variable_name=context.variable_name if context else None,
                    suggestion="Use just the secret name without namespace prefix"
                )
            
            namespace, secret_name = value.split('/', 1)
            
            # Validate namespace
            if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', namespace):
                raise ValidationError(
                    f"Invalid Kubernetes namespace: {namespace}",
                    variable_name=context.variable_name if context else None,
                    suggestion="Namespace names can contain lowercase letters, numbers, and hyphens"
                )
        else:
            secret_name = value
        
        # Validate secret name
        if not re.match(r'^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$', secret_name):
            raise ValidationError(
                "Invalid Kubernetes secret name format",
                variable_name=context.variable_name if context else None,
                suggestion="Secret names can contain lowercase letters, numbers, hyphens, and dots. Start and end with a letter or number"
            )
        
        # Check length
        if len(secret_name) > 253:
            raise ValidationError(
                f"Kubernetes secret name too long: {len(secret_name)} characters (max 253)",
                variable_name=context.variable_name if context else None,
                suggestion="Shorten the secret name to 253 characters or less"
            )
        
        return value 