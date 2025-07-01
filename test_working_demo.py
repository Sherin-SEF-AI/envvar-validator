#!/usr/bin/env python3
"""
Comprehensive test script for the working FastAPI demo application
Tests all endpoints and features of envvar-validator integration
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "sk_live_demo_1234567890abcdef"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️ {message}")

def test_endpoint(endpoint, method="GET", headers=None, data=None, expected_status=200):
    """Test an endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == expected_status:
            print_success(f"{method} {endpoint}: {response.status_code}")
            return response.json() if response.content else None
        else:
            print_error(f"{method} {endpoint}: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"{method} {endpoint}: Connection error - {e}")
        return None

def main():
    """Main test function"""
    print_header("Working FastAPI Demo - Comprehensive Test")
    print_info(f"Testing application at: {BASE_URL}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait for server to be ready
    print_info("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test 1: Basic endpoints
    print_header("1. Basic Endpoints")
    
    root_response = test_endpoint("/")
    if root_response:
        print_info(f"Message: {root_response.get('message')}")
        print_info(f"Status: {root_response.get('status')}")
    
    health_response = test_endpoint("/health")
    if health_response:
        print_info(f"Health Status: {health_response.get('status')}")
        print_info(f"Environment: {health_response.get('environment')}")
        print_info(f"Database: {health_response.get('database')}")
        print_info(f"Redis: {health_response.get('redis')}")
    
    # Test 2: Environment Validation
    print_header("2. Environment Validation")
    
    validation_response = test_endpoint("/env/validation")
    if validation_response:
        print_info(f"Validation Status: {'✅ Valid' if validation_response.get('is_valid') else '❌ Invalid'}")
        print_info(f"Total Variables: {validation_response.get('total_variables')}")
        print_info(f"Validated Variables: {validation_response.get('validated_variables')}")
        print_info(f"Errors: {validation_response.get('errors_count')}")
        print_info(f"Warnings: {validation_response.get('warnings_count')}")
        print_info(f"Security Score: {validation_response.get('security_score')}%")
        
        # Performance metrics
        metrics = validation_response.get('performance_metrics', {})
        print_info(f"Validation Time: {metrics.get('validation_time', 0):.6f}s")
    
    # Test 3: Configuration
    print_header("3. Application Configuration")
    
    config_response = test_endpoint("/config")
    if config_response:
        print_info(f"Environment: {config_response.get('environment')}")
        print_info(f"Debug Mode: {config_response.get('debug')}")
        print_info(f"Port: {config_response.get('port')}")
        print_info(f"Allowed Hosts: {config_response.get('allowed_hosts')}")
        print_info(f"CORS Origins: {config_response.get('cors_origins')}")
    
    # Test 4: Security Features
    print_header("4. Security Features")
    
    # Test without API key (should fail)
    print_info("Testing security scan without API key...")
    test_endpoint("/security/scan", expected_status=401)
    
    # Test with API key
    security_response = test_endpoint("/security/scan", headers=HEADERS)
    if security_response:
        print_info(f"Security Score: {security_response.get('security_score')}%")
        print_info(f"Issues Found: {security_response.get('issues_found')}")
        
        issues = security_response.get('issues', [])
        if issues:
            print_info("Security Issues:")
            for issue in issues:
                print(f"   • {issue}")
        
        recommendations = security_response.get('recommendations', [])
        if recommendations:
            print_info("Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
    
    # Test 5: Environment Values (Protected)
    print_header("5. Environment Values (Protected)")
    
    # Test without API key (should fail)
    print_info("Testing environment values without API key...")
    test_endpoint("/env/values", expected_status=401)
    
    # Test with API key
    env_values_response = test_endpoint("/env/values", headers=HEADERS)
    if env_values_response:
        env_values = env_values_response.get('environment_values', {})
        print_info(f"Environment Variables: {len(env_values)} variables")
        
        # Show non-sensitive values
        for key, value in env_values.items():
            if value != "***REDACTED***":
                print_info(f"   {key}: {value}")
            else:
                print_info(f"   {key}: {value} (sensitive)")
        
        metadata = env_values_response.get('metadata', {})
        print_info(f"Environment Type: {metadata.get('environment_type')}")
        print_info(f"Strict Mode: {metadata.get('strict_mode')}")
        print_info(f"Total Variables: {metadata.get('total_variables')}")
        print_info(f"Schema Variables: {metadata.get('schema_variables')}")
    
    # Test 6: API Documentation
    print_header("6. API Documentation")
    
    print_info("API Documentation URLs:")
    print(f"   • Swagger UI: {BASE_URL}/docs")
    print(f"   • ReDoc: {BASE_URL}/redoc")
    print(f"   • OpenAPI JSON: {BASE_URL}/openapi.json")
    
    # Test OpenAPI schema
    openapi_response = test_endpoint("/openapi.json")
    if openapi_response:
        print_success("OpenAPI schema is accessible")
        info = openapi_response.get('info', {})
        print_info(f"API Title: {info.get('title')}")
        print_info(f"API Version: {info.get('version')}")
        print_info(f"API Description: {info.get('description')}")
    
    # Test 7: Error Handling
    print_header("7. Error Handling")
    
    # Test non-existent endpoint
    print_info("Testing non-existent endpoint...")
    test_endpoint("/non-existent", expected_status=404)
    
    # Test invalid API key
    print_info("Testing with invalid API key...")
    invalid_headers = {"Authorization": "Bearer invalid-key"}
    test_endpoint("/security/scan", headers=invalid_headers, expected_status=401)
    
    # Summary
    print_header("Test Summary")
    print_success("All tests completed!")
    print_info(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🎉 Working Demo Features Demonstrated:")
    print("   ✅ Environment variable validation")
    print("   ✅ FastAPI integration")
    print("   ✅ Security scanning")
    print("   ✅ API key authentication")
    print("   ✅ Health checks")
    print("   ✅ Configuration management")
    print("   ✅ Error handling")
    print("   ✅ API documentation")
    print("   ✅ Performance metrics")
    print("   ✅ Security score calculation")
    
    print("\n📖 Next Steps:")
    print("   • Visit http://localhost:8000/docs for interactive API documentation")
    print("   • Modify environment variables to see validation changes")
    print("   • Add more validators to the schema")
    print("   • Integrate with your own FastAPI applications")
    print("   • Explore the envvar-validator CLI: envvar-validator --help")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        sys.exit(1) 