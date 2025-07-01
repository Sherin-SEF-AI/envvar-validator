#!/usr/bin/env python3
"""
Basic usage example for env-validator.

This example demonstrates how to use the env-validator package
to validate environment variables in a simple Python application.
"""

import os
from src.env_validator import EnvironmentValidator, ValidationError


def main():
    """Main function demonstrating basic usage."""
    
    # Define your environment validation schema
    schema = {
        "DATABASE_URL": {
            "type": "str",
            "required": True,
            "description": "Database connection URL",
            "examples": ["postgresql://user:pass@localhost/db", "sqlite:///app.db"]
        },
        "SECRET_KEY": {
            "type": "str",
            "required": True,
            "sensitive": True,
            "description": "Application secret key for security",
            "validators": ["secret_key"]
        },
        "DEBUG": {
            "type": "bool",
            "default": False,
            "description": "Debug mode flag"
        },
        "PORT": {
            "type": "int",
            "default": 8000,
            "description": "Application port number",
            "validators": ["port_range"]
        },
        "ALLOWED_HOSTS": {
            "type": "list",
            "default": ["localhost", "127.0.0.1"],
            "description": "List of allowed host names"
        },
        "EMAIL_HOST": {
            "type": "str",
            "required": False,
            "description": "Email server host",
            "validators": ["url"]
        }
    }
    
    # Create the validator
    validator = EnvironmentValidator(
        schema,
        environment_type="development",
        strict_mode=False,
        security_scanning=True
    )
    
    # Set up some example environment variables
    os.environ["DATABASE_URL"] = "postgresql://user:password@localhost/myapp"
    os.environ["SECRET_KEY"] = "your-super-secret-key-here-make-it-long-and-random"
    os.environ["DEBUG"] = "true"
    os.environ["PORT"] = "8080"
    os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1,example.com"
    os.environ["EMAIL_HOST"] = "https://smtp.example.com"
    
    print("🔍 Validating environment variables...")
    print("=" * 50)
    
    try:
        # Validate the environment
        result = validator.validate()
        
        if result.is_valid:
            print("✅ Environment validation passed!")
            print("\n📋 Validated Configuration:")
            print("-" * 30)
            
            for var_name, value in result.validated_values.items():
                # Mask sensitive values
                if var_name == "SECRET_KEY":
                    display_value = value[:8] + "***" + value[-8:] if len(value) > 16 else "***"
                else:
                    display_value = str(value)
                
                print(f"  {var_name}: {display_value}")
            
            # Show performance metrics
            if result.performance_metrics:
                print(f"\n⚡ Performance Metrics:")
                print("-" * 20)
                for metric, value in result.performance_metrics.items():
                    print(f"  {metric}: {value}")
            
            # Show security score if available
            if result.security_score:
                print(f"\n🔒 Security Score: {result.security_score}/100")
            
        else:
            print("❌ Environment validation failed!")
            print("\n🚨 Errors:")
            print("-" * 10)
            for error in result.errors:
                print(f"  • {error.variable_name}: {error.message}")
                if error.suggestion:
                    print(f"    💡 Suggestion: {error.suggestion}")
            
            if result.warnings:
                print("\n⚠️  Warnings:")
                print("-" * 12)
                for warning in result.warnings:
                    print(f"  • {warning.variable_name}: {warning.message}")
    
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        if hasattr(e, 'errors'):
            for error in e.errors:
                print(f"  • {error.variable_name}: {error.message}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_with_custom_validators():
    """Example showing how to use custom validators."""
    
    # Define a custom validator function
    def validate_api_version(value):
        """Custom validator for API version."""
        if not value.startswith("v"):
            raise ValueError("API version must start with 'v'")
        
        try:
            version_num = int(value[1:])
            if version_num < 1:
                raise ValueError("API version must be 1 or higher")
        except ValueError:
            raise ValueError("Invalid API version format")
        
        return value
    
    # Schema with custom validator
    schema = {
        "API_VERSION": {
            "type": "str",
            "required": True,
            "custom_validator": validate_api_version,
            "description": "API version (e.g., v1, v2)"
        }
    }
    
    validator = EnvironmentValidator(schema)
    
    # Test with valid version
    os.environ["API_VERSION"] = "v1"
    result = validator.validate()
    print(f"✅ API version validation: {result.validated_values['API_VERSION']}")
    
    # Test with invalid version
    os.environ["API_VERSION"] = "invalid"
    result = validator.validate()
    print(f"❌ API version validation failed: {len(result.errors)} errors")


def example_framework_integration():
    """Example showing framework integration."""
    
    # Django-like settings
    schema = {
        "SECRET_KEY": {
            "type": "str",
            "required": True,
            "sensitive": True,
            "validators": ["secret_key"]
        },
        "DATABASE_URL": {
            "type": "str",
            "required": True,
            "validators": ["database_url"]
        },
        "DEBUG": {
            "type": "bool",
            "default": False
        },
        "ALLOWED_HOSTS": {
            "type": "list",
            "default": ["localhost"]
        },
        "STATIC_URL": {
            "type": "str",
            "default": "/static/",
            "validators": ["url"]
        }
    }
    
    # Set up environment for Django
    os.environ["SECRET_KEY"] = "django-insecure-your-secret-key-here"
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/django_db"
    os.environ["DEBUG"] = "true"
    os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1"
    os.environ["STATIC_URL"] = "https://cdn.example.com/static/"
    
    validator = EnvironmentValidator(schema, environment_type="development")
    result = validator.validate()
    
    if result.is_valid:
        print("✅ Django environment validation passed!")
        
        # Use validated values in Django settings
        django_settings = {
            "SECRET_KEY": result.validated_values["SECRET_KEY"],
            "DEBUG": result.validated_values["DEBUG"],
            "ALLOWED_HOSTS": result.validated_values["ALLOWED_HOSTS"],
            "STATIC_URL": result.validated_values["STATIC_URL"]
        }
        
        print("📋 Django Settings:")
        for key, value in django_settings.items():
            if key == "SECRET_KEY":
                display_value = value[:8] + "***" + value[-8:]
            else:
                display_value = str(value)
            print(f"  {key}: {display_value}")


if __name__ == "__main__":
    print("🚀 env-validator Basic Usage Examples")
    print("=" * 50)
    
    # Run basic example
    print("\n1️⃣  Basic Environment Validation")
    main()
    
    # Run custom validator example
    print("\n\n2️⃣  Custom Validator Example")
    example_with_custom_validators()
    
    # Run framework integration example
    print("\n\n3️⃣  Framework Integration Example")
    example_framework_integration()
    
    print("\n\n🎉 All examples completed!")
    print("\nFor more examples and documentation, visit:")
    print("https://github.com/Sherin-SEF-AI/env-validator") 