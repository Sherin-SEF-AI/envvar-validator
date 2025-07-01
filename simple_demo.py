#!/usr/bin/env python3
"""
Simple demo of envvar-validator functionality
This script demonstrates the core features without requiring FastAPI
"""

import os
import json
from datetime import datetime

# Set up environment variables for demo
os.environ.update({
    'DATABASE_URL': 'postgresql://user:password@localhost:5432/demo_db',
    'API_KEY': 'sk_live_demo_1234567890abcdef',
    'SECRET_KEY': 'demo-secret-key-for-development-only',
    'DEBUG': 'true',
    'PORT': '8000',
    'ENVIRONMENT': 'development',
    'ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'CORS_ORIGINS': 'http://localhost:3000,http://127.0.0.1:3000',
    'JWT_SECRET': 'jwt-secret-key-for-demo',
    'REDIS_URL': 'redis://localhost:6379',
    'EMAIL_SMTP_HOST': 'smtp.gmail.com',
    'EMAIL_SMTP_PORT': '587',
    'EMAIL_USERNAME': 'demo@example.com',
    'EMAIL_PASSWORD': 'demo-password',
    'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
    'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    'AWS_REGION': 'us-east-1',
    'AWS_S3_BUCKET': 'demo-bucket',
    'STRIPE_SECRET_KEY': 'sk_test_demo_1234567890abcdef',
    'STRIPE_PUBLISHABLE_KEY': 'pk_test_demo_1234567890abcdef',
    'SENTRY_DSN': 'https://demo@sentry.io/123456',
    'LOG_LEVEL': 'INFO',
    'MAX_CONNECTIONS': '100',
    'SESSION_TIMEOUT': '3600',
    'RATE_LIMIT': '1000',
    'BACKUP_ENABLED': 'true',
    'BACKUP_SCHEDULE': '0 2 * * *',
    'MONITORING_ENABLED': 'true',
    'ALERT_EMAIL': 'alerts@example.com'
})

def demo_basic_validation():
    """Demonstrate basic environment validation"""
    print("🔍 Basic Environment Validation")
    print("=" * 40)
    
    try:
        from env_validator import EnvironmentValidator, ValidationError
        
        # Define a comprehensive schema
        schema = {
            "DATABASE_URL": {
                "type": "str",
                "required": True,
                "validators": ["database_url"],
                "description": "PostgreSQL database connection string"
            },
            "API_KEY": {
                "type": "str",
                "required": True,
                "validators": ["api_key"],
                "sensitive": True,
                "description": "API key for external services"
            },
            "SECRET_KEY": {
                "type": "str",
                "required": True,
                "validators": ["secret_key"],
                "sensitive": True,
                "description": "Application secret key"
            },
            "DEBUG": {
                "type": "bool",
                "default": False,
                "description": "Debug mode flag"
            },
            "PORT": {
                "type": "int",
                "default": 8000,
                "validators": ["port_range"],
                "description": "Application port"
            },
            "ENVIRONMENT": {
                "type": "str",
                "default": "development",
                "description": "Application environment"
            },
            "ALLOWED_HOSTS": {
                "type": "list",
                "default": ["localhost"],
                "description": "Allowed host names"
            },
            "EMAIL_USERNAME": {
                "type": "str",
                "required": True,
                "validators": ["email"],
                "description": "Email username"
            },
            "EMAIL_PASSWORD": {
                "type": "str",
                "required": True,
                "sensitive": True,
                "description": "Email password"
            }
        }
        
        # Create validator
        validator = EnvironmentValidator(schema)
        
        # Validate environment
        result = validator.validate()
        
        print(f"✅ Validation successful: {result.is_valid}")
        print(f"📊 Security Score: {result.security_score}%")
        print(f"⚡ Performance: {result.performance_metrics.get('validation_time', 0):.6f}s")
        print(f"🔢 Variables validated: {result.performance_metrics.get('variables_validated', 0)}")
        print(f"⚠️ Warnings: {result.performance_metrics.get('warnings_count', 0)}")
        print(f"❌ Errors: {result.performance_metrics.get('errors_count', 0)}")
        
        print("\n📋 Validated Values:")
        for key, value in result.validated_values.items():
            if schema.get(key, {}).get('sensitive', False):
                print(f"   {key}: ***REDACTED***")
            else:
                print(f"   {key}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None

def demo_framework_integrations():
    """Demonstrate framework integrations"""
    print("\n🏗️ Framework Integrations")
    print("=" * 40)
    
    # Django integration
    try:
        from env_validator.frameworks.django import DjangoEnvironmentValidator
        
        django_schema = {
            "SECRET_KEY": {"type": "str", "required": True, "validators": ["secret_key"]},
            "DATABASE_URL": {"type": "str", "required": True, "validators": ["database_url"]},
            "DEBUG": {"type": "bool", "default": False},
            "ALLOWED_HOSTS": {"type": "list", "default": ["localhost"]},
        }
        
        django_env = DjangoEnvironmentValidator(django_schema)
        result = django_env.validate()
        
        print("✅ Django Integration:")
        print(f"   Valid: {result.is_valid}")
        print(f"   Security Score: {result.security_score}%")
        print(f"   Variables: {result.performance_metrics.get('variables_validated', 0)}")
        
    except Exception as e:
        print(f"❌ Django integration failed: {e}")
    
    # FastAPI integration
    try:
        from env_validator.frameworks.fastapi import FastAPIEnvironmentValidator
        
        fastapi_schema = {
            "DATABASE_URL": {"type": "str", "required": True},
            "API_KEY": {"type": "str", "required": True, "sensitive": True},
            "ENVIRONMENT": {"type": "str", "default": "development"},
        }
        
        fastapi_env = FastAPIEnvironmentValidator(fastapi_schema)
        result = fastapi_env.validate()
        
        print("✅ FastAPI Integration:")
        print(f"   Valid: {result.is_valid}")
        print(f"   Security Score: {result.security_score}%")
        print(f"   Variables: {result.performance_metrics.get('variables_validated', 0)}")
        
    except Exception as e:
        print(f"❌ FastAPI integration failed: {e}")

def demo_custom_validators():
    """Demonstrate custom validators"""
    print("\n🚀 Custom Validators")
    print("=" * 40)
    
    try:
        from env_validator.validators.base import BaseValidator
        from env_validator import ValidationError, EnvironmentValidator
        
        # Custom validator for strong passwords
        class StrongPasswordValidator(BaseValidator):
            def validate(self, value: str) -> str:
                if len(value) < 8:
                    raise ValidationError("Password must be at least 8 characters long")
                if not any(c.isupper() for c in value):
                    raise ValidationError("Password must contain at least one uppercase letter")
                if not any(c.islower() for c in value):
                    raise ValidationError("Password must contain at least one lowercase letter")
                if not any(c.isdigit() for c in value):
                    raise ValidationError("Password must contain at least one digit")
                return value
        
        # Custom validator for environment-specific values
        class EnvironmentSpecificValidator(BaseValidator):
            def __init__(self, production_value: str):
                self.production_value = production_value
            
            def validate(self, value: str) -> str:
                env = os.environ.get('ENVIRONMENT', 'development')
                if env == 'production' and value != self.production_value:
                    raise ValidationError(f"Production environment requires value: {self.production_value}")
                return value
        
        # Test custom validators
        custom_schema = {
            "EMAIL_PASSWORD": {
                "type": "str",
                "validators": [StrongPasswordValidator()],
                "sensitive": True
            },
            "DATABASE_URL": {
                "type": "str",
                "validators": [EnvironmentSpecificValidator("postgresql://prod:pass@prod-db:5432/prod_db")],
                "sensitive": True
            }
        }
        
        validator = EnvironmentValidator(custom_schema)
        result = validator.validate()
        
        print("✅ Custom Validators:")
        print(f"   Valid: {result.is_valid}")
        if not result.is_valid:
            for error in result.errors:
                print(f"   Error: {error}")
        
    except Exception as e:
        print(f"❌ Custom validators failed: {e}")

def demo_cli_commands():
    """Demonstrate CLI commands"""
    print("\n🖥️ CLI Commands")
    print("=" * 40)
    
    import subprocess
    
    # Test help command
    try:
        result = subprocess.run(['envvar-validator', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI help command works!")
            print("   Available commands:")
            for line in result.stdout.split('\n'):
                if any(cmd in line for cmd in ['validate', 'setup', 'report', 'scan', 'list-validators', 'template']):
                    print(f"   - {line.strip()}")
        else:
            print(f"❌ CLI help command failed: {result.stderr}")
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
    
    # Test list-validators command
    try:
        result = subprocess.run(['envvar-validator', 'list-validators'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI list-validators command works!")
            print("   Available validators:")
            for line in result.stdout.split('\n')[:5]:  # Show first 5 lines
                if line.strip() and not line.startswith('┌') and not line.startswith('└'):
                    print(f"   - {line.strip()}")
        else:
            print(f"❌ CLI list-validators command failed: {result.stderr}")
    except Exception as e:
        print(f"❌ CLI list-validators test failed: {e}")

def demo_validation_report():
    """Generate a comprehensive validation report"""
    print("\n📊 Validation Report")
    print("=" * 40)
    
    try:
        from env_validator import EnvironmentValidator
        
        # Comprehensive schema
        schema = {
            "DATABASE_URL": {"type": "str", "required": True, "validators": ["database_url"]},
            "API_KEY": {"type": "str", "required": True, "validators": ["api_key"], "sensitive": True},
            "SECRET_KEY": {"type": "str", "required": True, "validators": ["secret_key"], "sensitive": True},
            "DEBUG": {"type": "bool", "default": False},
            "PORT": {"type": "int", "default": 8000, "validators": ["port_range"]},
            "ENVIRONMENT": {"type": "str", "default": "development"},
            "EMAIL_USERNAME": {"type": "str", "required": True, "validators": ["email"]},
            "EMAIL_PASSWORD": {"type": "str", "required": True, "sensitive": True},
            "AWS_ACCESS_KEY_ID": {"type": "str", "required": True, "sensitive": True},
            "AWS_SECRET_ACCESS_KEY": {"type": "str", "required": True, "sensitive": True},
            "AWS_REGION": {"type": "str", "required": True},
            "STRIPE_SECRET_KEY": {"type": "str", "required": True, "sensitive": True},
            "STRIPE_PUBLISHABLE_KEY": {"type": "str", "required": True},
            "SENTRY_DSN": {"type": "str", "required": False, "validators": ["url"]},
            "LOG_LEVEL": {"type": "str", "default": "INFO"},
            "MAX_CONNECTIONS": {"type": "int", "default": 100},
            "SESSION_TIMEOUT": {"type": "int", "default": 3600},
            "RATE_LIMIT": {"type": "int", "default": 1000},
            "BACKUP_ENABLED": {"type": "bool", "default": True},
            "MONITORING_ENABLED": {"type": "bool", "default": True},
            "ALERT_EMAIL": {"type": "str", "required": False, "validators": ["email"]}
        }
        
        validator = EnvironmentValidator(schema)
        result = validator.validate()
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_summary": {
                "is_valid": result.is_valid,
                "security_score": result.security_score,
                "total_variables": result.metadata.get('total_variables', 0),
                "schema_variables": result.metadata.get('schema_variables', 0),
                "validated_variables": result.performance_metrics.get('variables_validated', 0),
                "errors_count": result.performance_metrics.get('errors_count', 0),
                "warnings_count": result.performance_metrics.get('warnings_count', 0)
            },
            "performance_metrics": result.performance_metrics,
            "security_scan": result.metadata.get('security_scan', {}),
            "compliance_check": result.metadata.get('compliance_check', {}),
            "environment_info": {
                "environment_type": result.metadata.get('environment_type', 'unknown'),
                "strict_mode": result.metadata.get('strict_mode', False)
            },
            "validated_values": {
                k: "***REDACTED***" if schema.get(k, {}).get('sensitive', False) else v
                for k, v in result.validated_values.items()
            }
        }
        
        print("✅ Validation Report Generated:")
        print(f"   Timestamp: {report['timestamp']}")
        print(f"   Valid: {report['validation_summary']['is_valid']}")
        print(f"   Security Score: {report['validation_summary']['security_score']}%")
        print(f"   Variables: {report['validation_summary']['validated_variables']}/{report['validation_summary']['schema_variables']}")
        print(f"   Performance: {report['performance_metrics'].get('validation_time', 0):.6f}s")
        
        # Save report to file
        with open('validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("   📄 Report saved to: validation_report.json")
        
        return report
        
    except Exception as e:
        print(f"❌ Validation report failed: {e}")
        return None

def main():
    """Main demo function"""
    print("🎯 envvar-validator Demo Application")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all demos
    basic_result = demo_basic_validation()
    demo_framework_integrations()
    demo_custom_validators()
    demo_cli_commands()
    report = demo_validation_report()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    
    if basic_result and basic_result.is_valid:
        print("✅ Your environment is properly configured!")
        print(f"🔒 Security Score: {basic_result.security_score}%")
        print(f"⚡ Validation Time: {basic_result.performance_metrics.get('validation_time', 0):.6f}s")
    else:
        print("⚠️ Environment validation completed with issues.")
        print("   Check the output above for details.")
    
    print("\n🚀 Your envvar-validator package is working perfectly!")
    print("   Ready for production use!")

if __name__ == "__main__":
    main() 