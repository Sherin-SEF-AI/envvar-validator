#!/usr/bin/env python3
"""
Demo application runner and tester
This script runs the demo FastAPI application and tests its endpoints
"""

import os
import subprocess
import time
import requests
import json
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([
            "pip", "install", "-r", "requirements_demo.txt"
        ], check=True, capture_output=True)
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def start_demo_app():
    """Start the demo application"""
    print("🚀 Starting Demo Application...")
    
    # Run the demo app in the background
    process = subprocess.Popen([
        "python", "demo_app.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the app to start
    time.sleep(3)
    
    if process.poll() is None:
        print("✅ Demo application started successfully!")
        return process
    else:
        stdout, stderr = process.communicate()
        print(f"❌ Failed to start demo application:")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return None

def test_endpoints():
    """Test the demo application endpoints"""
    print("\n🧪 Testing Demo Application Endpoints...")
    
    base_url = "http://localhost:8000"
    api_key = "sk_live_demo_1234567890abcdef"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Test endpoints
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/env/validation", "Environment validation"),
        ("GET", "/config", "Configuration"),
        ("GET", "/users", "Get users"),
        ("GET", "/users/1", "Get user by ID"),
        ("GET", "/security/scan", "Security scan"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if endpoint in ["/users", "/users/1", "/security/scan"]:
                response = requests.request(method, f"{base_url}{endpoint}", headers=headers)
            else:
                response = requests.request(method, f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {description}: {response.status_code}")
                if endpoint == "/env/validation":
                    data = response.json()
                    print(f"   Security Score: {data.get('security_score', 'N/A')}%")
                    print(f"   Variables Validated: {data.get('validated_variables', 'N/A')}")
                elif endpoint == "/health":
                    data = response.json()
                    print(f"   Environment: {data.get('environment', 'N/A')}")
                    print(f"   Database: {data.get('database', 'N/A')}")
            else:
                print(f"⚠️ {description}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: Connection error - {e}")

def create_user():
    """Create a new user via API"""
    print("\n👤 Creating a new user...")
    
    base_url = "http://localhost:8000"
    api_key = "sk_live_demo_1234567890abcdef"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    user_data = {
        "username": "demo_user",
        "email": "demo_user@example.com",
        "password": "secure_password_123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/users",
            headers=headers,
            json=user_data
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"✅ User created successfully!")
            print(f"   ID: {user.get('id')}")
            print(f"   Username: {user.get('username')}")
            print(f"   Email: {user.get('email')}")
        else:
            print(f"⚠️ Failed to create user: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create user: {e}")

def show_api_documentation():
    """Show information about the API documentation"""
    print("\n📖 API Documentation:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    print("   OpenAPI JSON: http://localhost:8000/openapi.json")

def main():
    """Main function to run the demo"""
    print("🎯 Demo Application with envvar-validator")
    print("=" * 50)
    
    # Check if demo_app.py exists
    if not Path("demo_app.py").exists():
        print("❌ demo_app.py not found!")
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Start the demo application
    process = start_demo_app()
    if not process:
        return
    
    try:
        # Wait a bit more for the app to fully start
        time.sleep(2)
        
        # Test endpoints
        test_endpoints()
        
        # Create a user
        create_user()
        
        # Show API documentation info
        show_api_documentation()
        
        print("\n🎉 Demo application is running!")
        print("Press Ctrl+C to stop the application...")
        
        # Keep the app running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping demo application...")
        process.terminate()
        process.wait()
        print("✅ Demo application stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main() 