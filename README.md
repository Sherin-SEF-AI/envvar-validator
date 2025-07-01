# 🚀 env-validator

**The most comprehensive, production-ready environment variable validation library for Python**

[![PyPI version](https://badge.fury.io/py/env-validator.svg)](https://badge.fury.io/py/env-validator)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/Sherin-SEF-AI/env-validator/workflows/Tests/badge.svg)](https://github.com/Sherin-SEF-AI/env-validator/actions)
[![Documentation](https://readthedocs.org/projects/env-validator/badge/?version=latest)](https://env-validator.readthedocs.io/)

> **The definitive solution for Python environment variable validation that developers choose because it's genuinely the best tool available.**

## 🌟 Why env-validator?

**env-validator** is the most comprehensive, feature-rich environment variable validation library for Python. Built with production-ready features, security-first design, and exceptional developer experience, it's the tool that will revolutionize how you manage environment variables.

### ✨ Key Features

- 🔒 **Advanced Security**: Secret scanning, compliance validation, encryption key verification
- 🚀 **Framework Integration**: Seamless Django, Flask, FastAPI support
- 📊 **Monitoring & Observability**: Health checks, drift detection, performance metrics
- 🛠️ **Developer Tools**: CLI, interactive setup, codebase scanning
- 🏗️ **Team Collaboration**: Shared templates, audit logging, change notifications
- 🔧 **Extensible Architecture**: Plugin system, custom validators, middleware support
- 📱 **Cross-Platform**: Windows, macOS, Linux support
- 🎯 **Zero Configuration**: Works out of the box with sensible defaults

## 🚀 Quick Start

### Installation

```bash
pip install env-validator
```

### Basic Usage

```python
from env_validator import EnvironmentValidator, ValidationError

# Define your environment schema
validator = EnvironmentValidator({
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
    }
})

# Validate your environment
try:
    config = validator.validate()
    print(f"✅ Environment validated successfully!")
    print(f"Database: {config.DATABASE_URL}")
    print(f"Debug mode: {config.DEBUG}")
except ValidationError as e:
    print(f"❌ Environment validation failed: {e}")
```

### Framework Integration

#### Django
```python
# settings.py
from env_validator import DjangoEnvironmentValidator

env = DjangoEnvironmentValidator({
    "SECRET_KEY": {"type": "str", "required": True, "validators": ["secret_key"]},
    "DATABASE_URL": {"type": "str", "required": True, "validators": ["database_url"]},
    "DEBUG": {"type": "bool", "default": False},
    "ALLOWED_HOSTS": {"type": "list", "default": ["localhost"]},
})

# Validate and load environment
config = env.validate()

SECRET_KEY = config.SECRET_KEY
DATABASES = {
    'default': env.parse_database_url(config.DATABASE_URL)
}
DEBUG = config.DEBUG
ALLOWED_HOSTS = config.ALLOWED_HOSTS
```

#### FastAPI
```python
# config.py
from env_validator import FastAPIEnvironmentValidator
from pydantic import BaseSettings

class Settings(BaseSettings):
    env_validator = FastAPIEnvironmentValidator({
        "DATABASE_URL": {"type": "str", "required": True},
        "API_KEY": {"type": "str", "required": True, "sensitive": True},
        "ENVIRONMENT": {"type": "str", "default": "development"},
    })
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.env_validator.validate()

settings = Settings()
```

## 🛠️ CLI Tools

### Environment Validation
```bash
# Validate current environment
env-validator validate

# Validate with custom schema file
env-validator validate --schema schema.yaml

# Generate environment report
env-validator report --output html
```

### Interactive Setup
```bash
# Interactive environment setup wizard
env-validator setup

# Generate configuration templates
env-validator template --framework django
```

### Security Scanning
```bash
# Scan for secrets and sensitive data
env-validator scan --secrets

# Compliance check
env-validator scan --compliance gdpr
```

## 🔧 Advanced Features

### Custom Validators
```python
from env_validator import BaseValidator, ValidationError

class CustomAPIValidator(BaseValidator):
    def validate(self, value: str) -> str:
        if not value.startswith("api_"):
            raise ValidationError("API key must start with 'api_'")
        return value

validator = EnvironmentValidator({
    "API_KEY": {
        "type": "str",
        "validators": [CustomAPIValidator()]
    }
})
```

### Environment-Specific Configurations
```python
validator = EnvironmentValidator({
    "DATABASE_URL": {
        "type": "str",
        "required": True,
        "environments": {
            "development": "sqlite:///dev.db",
            "staging": {"type": "str", "validators": ["database_url"]},
            "production": {"type": "str", "validators": ["database_url", "ssl_required"]}
        }
    }
})
```

### Monitoring Integration
```python
from env_validator import MonitoringValidator

# Health check endpoint
@app.get("/health/env")
async def environment_health():
    return MonitoringValidator.health_check()

# Metrics endpoint
@app.get("/metrics/env")
async def environment_metrics():
    return MonitoringValidator.get_metrics()
```

## 📊 Built-in Validators

### Security Validators
- `secret_key`: Validates secret key strength and entropy
- `api_key`: Validates API key format and security
- `encryption_key`: Validates encryption key requirements
- `password_strength`: Checks password complexity requirements

### Network Validators
- `url`: Validates URL format and accessibility
- `ip_address`: Validates IPv4/IPv6 addresses
- `port_range`: Validates port numbers
- `database_url`: Validates database connection strings

### Data Validators
- `email`: RFC-compliant email validation
- `json`: JSON format validation
- `file_path`: File path existence and permissions
- `directory_path`: Directory existence and permissions

### Cloud Validators
- `aws_arn`: AWS ARN format validation
- `gcp_project_id`: Google Cloud project ID validation
- `azure_resource_id`: Azure resource identifier validation

## 🔒 Security Features

### Secret Detection
```python
validator = EnvironmentValidator({
    "API_KEY": {
        "type": "str",
        "sensitive": True,
        "validators": ["secret_scanning"]
    }
})

# Automatically detects and protects sensitive values
config = validator.validate()
print(config.API_KEY)  # Shows: "***REDACTED***"
```

### Compliance Validation
```python
validator = EnvironmentValidator({
    "PII_DATA": {
        "type": "str",
        "compliance": ["gdpr", "hipaa"],
        "encryption": "required"
    }
})
```

## 📈 Monitoring & Observability

### Health Checks
```python
from env_validator import HealthChecker

# Check environment health
health = HealthChecker.check()
if not health.is_healthy:
    print(f"Environment issues: {health.issues}")
```

### Drift Detection
```python
from env_validator import DriftDetector

# Detect configuration drift
drift = DriftDetector.detect()
if drift.has_changes:
    print(f"Configuration drift detected: {drift.changes}")
```

## 🏗️ Framework Integrations

### Django
```python
# settings.py
from env_validator.django import DjangoEnvironmentValidator

env = DjangoEnvironmentValidator.from_settings_file()
config = env.validate()

# Automatic Django settings integration
SECRET_KEY = config.SECRET_KEY
DATABASES = config.DATABASES
```

### Flask
```python
# app.py
from env_validator.flask import FlaskEnvironmentValidator

app = Flask(__name__)
env = FlaskEnvironmentValidator(app, {
    "SECRET_KEY": {"type": "str", "required": True},
    "DATABASE_URL": {"type": "str", "required": True},
})
```

### FastAPI
```python
# main.py
from env_validator.fastapi import FastAPIEnvironmentValidator

app = FastAPI()
env = FastAPIEnvironmentValidator(app, {
    "API_KEY": {"type": "str", "required": True},
    "DATABASE_URL": {"type": "str", "required": True},
})
```

## 🚀 Performance Features

- **Lazy Loading**: Validators load only when needed
- **Caching**: Repeated validations are cached
- **Async Support**: Non-blocking validation operations
- **Memory Efficient**: Minimal memory footprint

## 📚 Documentation

- [📖 Full Documentation](https://env-validator.readthedocs.io/)
- [🚀 Quick Start Guide](https://env-validator.readthedocs.io/en/latest/quickstart.html)
- [🔧 API Reference](https://env-validator.readthedocs.io/en/latest/api.html)
- [🏗️ Framework Integrations](https://env-validator.readthedocs.io/en/latest/frameworks.html)
- [🔒 Security Guide](https://env-validator.readthedocs.io/en/latest/security.html)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/Sherin-SEF-AI/env-validator.git
cd env-validator
pip install -e ".[dev]"
pre-commit install
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ by the Python community
- Inspired by the need for better environment variable management
- Thanks to all contributors and users

## 📊 Project Status

- ✅ Core validation engine
- ✅ Advanced validators library
- ✅ Framework integrations
- ✅ CLI tools
- ✅ Security features
- ✅ Monitoring & observability
- ✅ Documentation
- ✅ Testing suite
- 🚧 Community features
- 🚧 Performance optimizations

---

**Made with ❤️ by [Sherin Joseph Roy](https://github.com/Sherin-SEF-AI)**

[GitHub](https://github.com/Sherin-SEF-AI/env-validator) | [Documentation](https://env-validator.readthedocs.io/) | [Issues](https://github.com/Sherin-SEF-AI/env-validator/issues) | [Discussions](https://github.com/Sherin-SEF-AI/env-validator/discussions) 