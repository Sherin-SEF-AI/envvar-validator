#!/usr/bin/env python3
"""
Real-world FastAPI application demonstrating envvar-validator
This is a complete web application with proper environment validation
"""

import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Environment validation
from env_validator.frameworks.fastapi import FastAPIEnvironmentValidator

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

# Pydantic models
class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

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
    # Database configuration
    "DATABASE_URL": {
        "type": "str",
        "required": True,
        "validators": ["database_url"],
        "description": "PostgreSQL database connection string"
    },
    
    # API and Security
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
    "JWT_SECRET": {
        "type": "str",
        "required": True,
        "validators": ["secret_key"],
        "sensitive": True,
        "description": "JWT signing secret"
    },
    
    # Application settings
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
        "validators": ["enum"],
        "enum_values": ["development", "staging", "production"],
        "description": "Application environment"
    },
    
    # Hosting and CORS
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
    
    # External services
    "REDIS_URL": {
        "type": "str",
        "required": True,
        "validators": ["database_url"],
        "description": "Redis connection URL"
    },
    
    # Email configuration
    "EMAIL_SMTP_HOST": {
        "type": "str",
        "required": True,
        "description": "SMTP server host"
    },
    "EMAIL_SMTP_PORT": {
        "type": "int",
        "required": True,
        "validators": ["port_range"],
        "description": "SMTP server port"
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
    },
    
    # AWS configuration
    "AWS_ACCESS_KEY_ID": {
        "type": "str",
        "required": True,
        "validators": ["aws_access_key"],
        "sensitive": True,
        "description": "AWS access key ID"
    },
    "AWS_SECRET_ACCESS_KEY": {
        "type": "str",
        "required": True,
        "validators": ["aws_secret_key"],
        "sensitive": True,
        "description": "AWS secret access key"
    },
    "AWS_REGION": {
        "type": "str",
        "required": True,
        "validators": ["aws_region"],
        "description": "AWS region"
    },
    "AWS_S3_BUCKET": {
        "type": "str",
        "required": True,
        "description": "AWS S3 bucket name"
    },
    
    # Payment processing
    "STRIPE_SECRET_KEY": {
        "type": "str",
        "required": True,
        "validators": ["stripe_secret_key"],
        "sensitive": True,
        "description": "Stripe secret key"
    },
    "STRIPE_PUBLISHABLE_KEY": {
        "type": "str",
        "required": True,
        "validators": ["stripe_publishable_key"],
        "description": "Stripe publishable key"
    },
    
    # Monitoring and logging
    "SENTRY_DSN": {
        "type": "str",
        "required": False,
        "validators": ["url"],
        "description": "Sentry DSN for error tracking"
    },
    "LOG_LEVEL": {
        "type": "str",
        "default": "INFO",
        "validators": ["enum"],
        "enum_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "description": "Logging level"
    },
    
    # Performance and limits
    "MAX_CONNECTIONS": {
        "type": "int",
        "default": 100,
        "validators": ["positive_integer"],
        "description": "Maximum database connections"
    },
    "SESSION_TIMEOUT": {
        "type": "int",
        "default": 3600,
        "validators": ["positive_integer"],
        "description": "Session timeout in seconds"
    },
    "RATE_LIMIT": {
        "type": "int",
        "default": 1000,
        "validators": ["positive_integer"],
        "description": "Rate limit per hour"
    },
    
    # Backup and monitoring
    "BACKUP_ENABLED": {
        "type": "bool",
        "default": True,
        "description": "Enable automated backups"
    },
    "BACKUP_SCHEDULE": {
        "type": "str",
        "default": "0 2 * * *",
        "validators": ["cron_expression"],
        "description": "Backup schedule (cron expression)"
    },
    "MONITORING_ENABLED": {
        "type": "bool",
        "default": True,
        "description": "Enable application monitoring"
    },
    "ALERT_EMAIL": {
        "type": "str",
        "required": False,
        "validators": ["email"],
        "description": "Email for monitoring alerts"
    }
}

# Initialize FastAPI app with environment validation
app = FastAPI(
    title="Demo Application with envvar-validator",
    description="A real-world FastAPI application demonstrating comprehensive environment variable validation",
    version="1.0.0"
)

# Initialize environment validator
env_validator = FastAPIEnvironmentValidator(ENV_SCHEMA)

# Validate environment on startup
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

# Security
security = HTTPBearer()

# Mock database
users_db = [
    User(
        id=1,
        username="admin",
        email="admin@example.com",
        is_active=True,
        created_at=datetime.now() - timedelta(days=30)
    ),
    User(
        id=2,
        username="user1",
        email="user1@example.com",
        is_active=True,
        created_at=datetime.now() - timedelta(days=15)
    )
]

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
        "message": "Welcome to Demo Application with envvar-validator!",
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
        errors_count=result.performance_metrics.get('errors_count', 0),
        warnings_count=result.performance_metrics.get('warnings_count', 0),
        security_score=result.security_score,
        performance_metrics=result.performance_metrics
    )

@app.get("/env/values")
async def get_env_values(api_key: str = Depends(verify_api_key)):
    """Get environment values (requires API key)"""
    env = get_env()
    
    # Return non-sensitive values only
    safe_values = {}
    for key, value in env.validated_values.items():
        if not env.schema.get(key, {}).get('sensitive', False):
            safe_values[key] = value
        else:
            safe_values[key] = "***REDACTED***"
    
    return {
        "environment_values": safe_values,
        "metadata": env.metadata,
        "security_score": env.security_score
    }

@app.get("/users", response_model=List[UserResponse])
async def get_users(api_key: str = Depends(verify_api_key)):
    """Get all users (requires API key)"""
    return [UserResponse(**user.dict()) for user in users_db]

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, api_key: str = Depends(verify_api_key)):
    """Get user by ID (requires API key)"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user.dict())

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, api_key: str = Depends(verify_api_key)):
    """Create new user (requires API key)"""
    # Check if user already exists
    if any(u.username == user.username for u in users_db):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(
        id=len(users_db) + 1,
        username=user.username,
        email=user.email,
        is_active=True,
        created_at=datetime.now()
    )
    users_db.append(new_user)
    
    return UserResponse(**new_user.dict())

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

# Add CORS middleware
@app.on_event("startup")
async def setup_cors():
    """Setup CORS middleware"""
    env = get_env()
    cors_origins = env.validated_values.get('CORS_ORIGINS', [])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get validated port
    env = env_validator.validate()
    port = env.validated_values.get('PORT', 8000)
    
    print(f"🚀 Starting Demo Application on port {port}")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print(f"⚙️ Environment Validation: http://localhost:{port}/env/validation")
    
    uvicorn.run(
        "demo_app:app",
        host="0.0.0.0",
        port=port,
        reload=env.validated_values.get('DEBUG', False)
    ) 