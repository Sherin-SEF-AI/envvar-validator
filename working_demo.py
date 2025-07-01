#!/usr/bin/env python3
"""
Working FastAPI demo application with envvar-validator
Simplified version that focuses on core functionality
"""

import os
from datetime import datetime
from typing import Dict, Any

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

try:
    from fastapi import FastAPI, HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel
    from env_validator.frameworks.fastapi import FastAPIEnvironmentValidator
    
    # Pydantic models
    class HealthCheck(BaseModel):
        status: str
        timestamp: datetime
        environment: str
        database: str
        redis: str
        version: str

    class ValidationReport(BaseModel):
        is_valid: bool
        total_variables: int
        validated_variables: int
        errors_count: int
        warnings_count: int
        security_score: float
        performance_metrics: Dict[str, Any]

    # Environment validation schema
    ENV_SCHEMA = {
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
        "CORS_ORIGINS": {
            "type": "list",
            "default": ["http://localhost:3000"],
            "description": "CORS allowed origins"
        },
        "REDIS_URL": {
            "type": "str",
            "required": True,
            "validators": ["database_url"],
            "description": "Redis connection URL"
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

    # Initialize FastAPI app
    app = FastAPI(
        title="Working Demo with envvar-validator",
        description="A working FastAPI application demonstrating environment variable validation",
        version="1.0.0"
    )

    # Initialize environment validator
    env_validator = FastAPIEnvironmentValidator(ENV_SCHEMA)

    # Security
    security = HTTPBearer()

    # Dependency to get validated environment
    def get_env():
        """Get validated environment variables"""
        return env_validator.validate()

    # Dependency to verify API key
    async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify API key from request"""
        env = get_env()
        expected_api_key = env.validated_values.get('API_KEY')
        
        if credentials.credentials != expected_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        return credentials.credentials

    # Routes
    @app.get("/", response_model=Dict[str, str])
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to Working Demo with envvar-validator!",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }

    @app.get("/health", response_model=HealthCheck)
    async def health_check():
        """Health check endpoint"""
        env = get_env()
        
        return HealthCheck(
            status="healthy",
            timestamp=datetime.now(),
            environment=env.validated_values.get('ENVIRONMENT', 'unknown'),
            database="connected" if env.validated_values.get('DATABASE_URL') else "disconnected",
            redis="connected" if env.validated_values.get('REDIS_URL') else "disconnected",
            version="1.0.0"
        )

    @app.get("/env/validation", response_model=ValidationReport)
    async def get_validation_report():
        """Get environment validation report"""
        result = env_validator.validate()
        
        return ValidationReport(
            is_valid=result.is_valid,
            total_variables=result.metadata.get('total_variables', 0),
            validated_variables=result.metadata.get('schema_variables', 0),
            errors_count=int(result.performance_metrics.get('errors_count', 0)),
            warnings_count=int(result.performance_metrics.get('warnings_count', 0)),
            security_score=result.security_score or 0.0,
            performance_metrics=result.performance_metrics
        )

    @app.get("/config")
    async def get_config():
        """Get application configuration (non-sensitive)"""
        env = get_env()
        
        return {
            "environment": env.validated_values.get('ENVIRONMENT'),
            "debug": env.validated_values.get('DEBUG'),
            "port": env.validated_values.get('PORT'),
            "allowed_hosts": env.validated_values.get('ALLOWED_HOSTS'),
            "cors_origins": env.validated_values.get('CORS_ORIGINS'),
            "log_level": env.validated_values.get('LOG_LEVEL'),
            "max_connections": env.validated_values.get('MAX_CONNECTIONS'),
            "session_timeout": env.validated_values.get('SESSION_TIMEOUT'),
            "rate_limit": env.validated_values.get('RATE_LIMIT'),
            "backup_enabled": env.validated_values.get('BACKUP_ENABLED'),
            "monitoring_enabled": env.validated_values.get('MONITORING_ENABLED')
        }

    @app.get("/env/values")
    async def get_env_values(api_key: str = Depends(verify_api_key)):
        """Get environment values (requires API key)"""
        env = get_env()
        
        # Return non-sensitive values only
        safe_values = {}
        for key, value in env.validated_values.items():
            if not ENV_SCHEMA.get(key, {}).get('sensitive', False):
                safe_values[key] = value
            else:
                safe_values[key] = "***REDACTED***"
        
        return {
            "environment_values": safe_values,
            "metadata": env.metadata,
            "security_score": env.security_score
        }

    @app.get("/security/scan")
    async def security_scan(api_key: str = Depends(verify_api_key)):
        """Perform security scan (requires API key)"""
        env = get_env()
        
        # Simulate security scan
        security_issues = []
        
        # Check for weak secrets
        if env.validated_values.get('SECRET_KEY', '').startswith('demo-'):
            security_issues.append("Weak secret key detected")
        
        if env.validated_values.get('JWT_SECRET', '').startswith('jwt-'):
            security_issues.append("Weak JWT secret detected")
        
        # Check for development environment in production-like settings
        if env.validated_values.get('ENVIRONMENT') == 'development':
            if env.validated_values.get('DEBUG'):
                security_issues.append("Debug mode enabled in development")
        
        return {
            "security_score": env.security_score,
            "issues_found": len(security_issues),
            "issues": security_issues,
            "recommendations": [
                "Use strong, randomly generated secrets",
                "Disable debug mode in production",
                "Use environment-specific configurations",
                "Regularly rotate API keys and secrets"
            ]
        }

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Validate environment variables on application startup"""
        try:
            result = env_validator.validate()
            if not result.is_valid:
                print(f"❌ Environment validation failed: {result.errors}")
                raise Exception("Environment validation failed")
            
            print("✅ Environment validation successful!")
            print(f"   Environment: {result.validated_values.get('ENVIRONMENT', 'unknown')}")
            print(f"   Debug mode: {result.validated_values.get('DEBUG', False)}")
            print(f"   Security score: {result.security_score}%")
            print(f"   Variables validated: {result.performance_metrics.get('variables_validated', 0)}")
            
        except Exception as e:
            print(f"❌ Failed to validate environment: {e}")
            raise

    if __name__ == "__main__":
        import uvicorn
        
        # Get validated port
        env = env_validator.validate()
        port = env.validated_values.get('PORT', 8000)
        
        print(f"🚀 Starting Working Demo Application on port {port}")
        print(f"📖 API Documentation: http://localhost:{port}/docs")
        print(f"🔍 Health Check: http://localhost:{port}/health")
        print(f"⚙️ Environment Validation: http://localhost:{port}/env/validation")
        
        uvicorn.run(
            "working_demo:app",
            host="0.0.0.0",
            port=port,
            reload=env.validated_values.get('DEBUG', False)
        )

except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please install FastAPI and uvicorn:")
    print("pip install fastapi uvicorn")
    
    # Fallback to simple demo
    print("\n🔄 Running simple demo instead...")
    import subprocess
    subprocess.run(["python", "simple_demo.py"]) 