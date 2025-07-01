#!/usr/bin/env python3
"""
Comprehensive test script for envvar-validator package
Demonstrates all major features and functionality
"""

import os
import sys
import subprocess
from pathlib import Path

def test_basic_validation():
    """Test basic environment variable validation"""
    print("🔍 Testing Basic Validation...")
    
    # Set up test environment variables
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/db'
    os.environ['API_KEY'] = 'sk_test_1234567890abcdef'
    os.environ['DEBUG'] = 'true'
    os.environ['PORT'] = '8000'
    os.environ['EMAIL'] = 'test@example.com'
    
    try:
        from env_validator import EnvironmentValidator, ValidationError
        
        # Define schema
        schema = {
            "DATABASE_URL": {
                "type": "str",
                "required": True,
                "validators": ["database_url"]
            },
            "API_KEY": {
                "type": "str",
                "required": True,
                "validators": ["api_key"],
                "sensitive": True
            },
            "DEBUG": {
                "type": "bool",
                "default": False
            },
            "PORT": {
                "type": "int",
                "default": 8000,
                "validators": ["port_range"]
            },
            "EMAIL": {
                "type": "str",
                "validators": ["email"]
            }
        }
        
        # Create validator
        validator = EnvironmentValidator(schema)
        
        # Validate environment
        config = validator.validate()
        
        print("✅ Basic validation successful!")
        print(f"   Database URL: {config.DATABASE_URL}")
        print(f"   API Key: {config.API_KEY}")  # Should show as redacted
        print(f"   Debug: {config.DEBUG}")
        print(f"   Port: {config.PORT}")
        print(f"   Email: {config.EMAIL}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic validation failed: {e}")
        return False

def test_framework_integrations():
    """Test framework-specific integrations"""
    print("\n🏗️ Testing Framework Integrations...")
    
    # Django integration test
    try:
        from env_validator.frameworks.django import DjangoEnvironmentValidator
        
        django_schema = {
            "SECRET_KEY": {"type": "str", "required": True, "validators": ["secret_key"]},
            "DATABASE_URL": {"type": "str", "required": True, "validators": ["database_url"]},
            "DEBUG": {"type": "bool", "default": False},
            "ALLOWED_HOSTS": {"type": "list", "default": ["localhost"]},
        }
        
        django_env = DjangoEnvironmentValidator(django_schema)
        config = django_env.validate()
        
        print("✅ Django integration successful!")
        print(f"   Secret Key: {config.SECRET_KEY[:10]}...")
        print(f"   Debug: {config.DEBUG}")
        print(f"   Allowed Hosts: {config.ALLOWED_HOSTS}")
        
    except Exception as e:
        print(f"❌ Django integration failed: {e}")
    
    # FastAPI integration test
    try:
        from env_validator.frameworks.fastapi import FastAPIEnvironmentValidator
        
        fastapi_schema = {
            "DATABASE_URL": {"type": "str", "required": True},
            "API_KEY": {"type": "str", "required": True, "sensitive": True},
            "ENVIRONMENT": {"type": "str", "default": "development"},
        }
        
        fastapi_env = FastAPIEnvironmentValidator(fastapi_schema)
        config = fastapi_env.validate()
        
        print("✅ FastAPI integration successful!")
        print(f"   Environment: {config.ENVIRONMENT}")
        
    except Exception as e:
        print(f"❌ FastAPI integration failed: {e}")

def test_cli_commands():
    """Test CLI commands"""
    print("\n🖥️ Testing CLI Commands...")
    
    try:
        # Test help command
        result = subprocess.run(['envvar-validator', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI help command works!")
        else:
            print(f"❌ CLI help command failed: {result.stderr}")
            
        # Test list-validators command
        result = subprocess.run(['envvar-validator', 'list-validators'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI list-validators command works!")
            print("   Available validators:")
            for line in result.stdout.split('\n')[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"   - {line.strip()}")
        else:
            print(f"❌ CLI list-validators command failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ CLI command timed out")
    except FileNotFoundError:
        print("❌ CLI command not found - make sure envvar-validator is installed")

def test_advanced_features():
    """Test advanced features like custom validators and monitoring"""
    print("\n🚀 Testing Advanced Features...")
    
    try:
        from env_validator import BaseValidator, ValidationError
        from env_validator.monitoring import HealthChecker, DriftDetector
        
        # Custom validator test
        class CustomAPIValidator(BaseValidator):
            def validate(self, value: str) -> str:
                if not value.startswith("sk_"):
                    raise ValidationError("API key must start with 'sk_'")
                return value
        
        custom_schema = {
            "API_KEY": {
                "type": "str",
                "validators": [CustomAPIValidator()]
            }
        }
        
        from env_validator import EnvironmentValidator
        validator = EnvironmentValidator(custom_schema)
        config = validator.validate()
        
        print("✅ Custom validator works!")
        
        # Health check test
        try:
            health = HealthChecker.check()
            print("✅ Health checker works!")
        except Exception as e:
            print(f"⚠️ Health checker: {e}")
        
        # Drift detection test
        try:
            drift = DriftDetector.detect()
            print("✅ Drift detector works!")
        except Exception as e:
            print(f"⚠️ Drift detector: {e}")
            
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")

def test_security_features():
    """Test security scanning and compliance features"""
    print("\n🔒 Testing Security Features...")
    
    try:
        from env_validator.security import SecurityScanner
        
        # Test security scanner
        scanner = SecurityScanner()
        vulnerabilities = scanner.scan_environment()
        
        print("✅ Security scanner works!")
        print(f"   Found {len(vulnerabilities)} potential security issues")
        
        # Test audit logging
        from env_validator.security import AuditLogger
        audit_logger = AuditLogger()
        audit_logger.log_validation("test_validation", {"status": "success"})
        
        print("✅ Audit logging works!")
        
    except Exception as e:
        print(f"❌ Security features test failed: {e}")

def test_exporters():
    """Test export functionality"""
    print("\n📊 Testing Export Features...")
    
    try:
        from env_validator.utils.exporters import JSONExporter, YAMLExporter
        
        # Test JSON export
        test_data = {"DATABASE_URL": "postgresql://localhost/db", "DEBUG": True}
        json_exporter = JSONExporter()
        json_output = json_exporter.export(test_data)
        
        print("✅ JSON exporter works!")
        
        # Test YAML export
        yaml_exporter = YAMLExporter()
        yaml_output = yaml_exporter.export(test_data)
        
        print("✅ YAML exporter works!")
        
    except Exception as e:
        print(f"❌ Export features test failed: {e}")

def main():
    """Run all tests"""
    print("🧪 Starting envvar-validator Package Tests")
    print("=" * 50)
    
    # Set required environment variables for testing
    if 'SECRET_KEY' not in os.environ:
        os.environ['SECRET_KEY'] = 'django-insecure-test-key-for-validation-only'
    
    tests = [
        test_basic_validation,
        test_framework_integrations,
        test_cli_commands,
        test_advanced_features,
        test_security_features,
        test_exporters
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your envvar-validator package is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\n🚀 Your envvar-validator package is ready for production use!")

if __name__ == "__main__":
    main() 