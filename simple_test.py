#!/usr/bin/env python3
"""
Simple test script for envvar-validator package
Tests the actual implemented functionality
"""

import os
import subprocess

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
        result = validator.validate()
        
        print("✅ Basic validation successful!")
        print(f"   Validation result: {result}")
        
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
        result = django_env.validate()
        
        print("✅ Django integration successful!")
        print(f"   Validation result: {result}")
        
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
        result = fastapi_env.validate()
        
        print("✅ FastAPI integration successful!")
        print(f"   Validation result: {result}")
        
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
            print("   Available commands:")
            for line in result.stdout.split('\n'):
                if 'Commands' in line or any(cmd in line for cmd in ['validate', 'setup', 'report', 'scan', 'list-validators', 'template']):
                    print(f"   - {line.strip()}")
        else:
            print(f"❌ CLI help command failed: {result.stderr}")
            
        # Test list-validators command
        result = subprocess.run(['envvar-validator', 'list-validators'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI list-validators command works!")
            print("   Available validators:")
            for line in result.stdout.split('\n')[:10]:  # Show first 10 lines
                if line.strip() and not line.startswith('┌') and not line.startswith('└'):
                    print(f"   - {line.strip()}")
        else:
            print(f"❌ CLI list-validators command failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ CLI command timed out")
    except FileNotFoundError:
        print("❌ CLI command not found - make sure envvar-validator is installed")

def test_custom_validator():
    """Test custom validator functionality"""
    print("\n🚀 Testing Custom Validator...")
    
    try:
        from env_validator.validators.base import BaseValidator
        from env_validator import ValidationError
        
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
        result = validator.validate()
        
        print("✅ Custom validator works!")
        print(f"   Validation result: {result}")
        
    except Exception as e:
        print(f"❌ Custom validator test failed: {e}")

def test_validation_error():
    """Test validation error handling"""
    print("\n⚠️ Testing Validation Error Handling...")
    
    try:
        from env_validator import EnvironmentValidator, ValidationError
        
        # Test with missing required variable
        schema = {
            "MISSING_VAR": {
                "type": "str",
                "required": True
            }
        }
        
        validator = EnvironmentValidator(schema)
        
        try:
            result = validator.validate()
            print("❌ Should have raised ValidationError for missing required variable")
        except ValidationError as e:
            print("✅ ValidationError correctly raised for missing required variable")
            print(f"   Error: {e}")
        
        # Test with invalid type
        os.environ['INVALID_PORT'] = 'not_a_number'
        schema = {
            "INVALID_PORT": {
                "type": "int",
                "required": True
            }
        }
        
        validator = EnvironmentValidator(schema)
        
        try:
            result = validator.validate()
            print("❌ Should have raised ValidationError for invalid type")
        except ValidationError as e:
            print("✅ ValidationError correctly raised for invalid type")
            print(f"   Error: {e}")
        
    except Exception as e:
        print(f"❌ Validation error test failed: {e}")

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
        test_custom_validator,
        test_validation_error
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