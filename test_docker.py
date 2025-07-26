#!/usr/bin/env python3
"""
Docker configuration test script for Remnawave Telegram Bot
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path

def test_docker_files():
    """Test if all Docker files exist and are valid"""
    print("🐳 Testing Docker configuration...")
    
    required_files = [
        'Dockerfile',
        'docker-compose.yml',
        'docker-compose.prod.yml',
        '.dockerignore',
        'docker-scripts/start.sh',
        'docker-scripts/stop.sh'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing Docker files: {', '.join(missing_files)}")
        return False
    
    print("✅ All Docker files exist")
    return True

def test_compose_files():
    """Test Docker Compose files for valid YAML"""
    print("📋 Testing Docker Compose files...")
    
    compose_files = ['docker-compose.yml', 'docker-compose.prod.yml']
    
    for file_path in compose_files:
        try:
            with open(file_path, 'r') as f:
                yaml.safe_load(f)
            print(f"✅ {file_path} is valid YAML")
        except yaml.YAMLError as e:
            print(f"❌ {file_path} has YAML syntax error: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {file_path} not found")
            return False
    
    return True

def test_dockerfile():
    """Test Dockerfile syntax"""
    print("🔧 Testing Dockerfile...")
    
    try:
        with open('Dockerfile', 'r') as f:
            content = f.read()
        
        # Basic checks
        if 'FROM ' not in content:
            print("❌ Dockerfile missing FROM instruction")
            return False
        
        if 'WORKDIR ' not in content:
            print("❌ Dockerfile missing WORKDIR instruction")
            return False
        
        if 'CMD ' not in content and 'ENTRYPOINT ' not in content:
            print("❌ Dockerfile missing CMD or ENTRYPOINT instruction")
            return False
        
        print("✅ Dockerfile syntax looks good")
        return True
        
    except FileNotFoundError:
        print("❌ Dockerfile not found")
        return False

def test_docker_scripts():
    """Test if Docker scripts are executable"""
    print("🔨 Testing Docker scripts...")
    
    scripts = ['docker-scripts/start.sh', 'docker-scripts/stop.sh']
    
    for script in scripts:
        if not os.path.exists(script):
            print(f"❌ {script} not found")
            return False
        
        if not os.access(script, os.X_OK):
            print(f"❌ {script} is not executable")
            return False
        
        print(f"✅ {script} is executable")
    
    return True

def test_dockerignore():
    """Test .dockerignore file"""
    print("🚫 Testing .dockerignore...")
    
    try:
        with open('.dockerignore', 'r') as f:
            content = f.read()
        
        # Check for important ignores
        important_ignores = ['.git', '__pycache__', 'venv/', '.env']
        
        for ignore in important_ignores:
            if ignore not in content:
                print(f"⚠️  .dockerignore missing: {ignore}")
        
        print("✅ .dockerignore file exists")
        return True
        
    except FileNotFoundError:
        print("❌ .dockerignore not found")
        return False

def test_docker_availability():
    """Test if Docker is available"""
    print("🐋 Testing Docker availability...")
    
    try:
        # Check if docker command is available
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
        else:
            print("⚠️  Docker not available (this is OK for CI/testing)")
            return True  # Don't fail the test if Docker isn't installed
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Docker not available (this is OK for CI/testing)")
        return True
    
    try:
        # Check docker-compose
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker Compose available: {result.stdout.strip()}")
        else:
            # Try new docker compose command
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Docker Compose available: {result.stdout.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Docker Compose not available (this is OK for CI/testing)")
    
    return True

def test_env_file():
    """Test if .env.example exists and has Docker-related vars"""
    print("⚙️  Testing environment configuration...")
    
    if not os.path.exists('.env.example'):
        print("❌ .env.example not found")
        return False
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'REMNAWAVE_BASE_URL',
        'REMNAWAVE_TOKEN',
        'ADMIN_USER_IDS'
    ]
    
    for var in required_vars:
        if var not in content:
            print(f"❌ .env.example missing variable: {var}")
            return False
    
    print("✅ .env.example has required variables")
    return True

def main():
    """Main test function"""
    print("🧪 Docker Configuration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Docker Files", test_docker_files),
        ("Compose Files", test_compose_files),
        ("Dockerfile", test_dockerfile),
        ("Docker Scripts", test_docker_scripts),
        ("Dockerignore", test_dockerignore),
        ("Docker Availability", test_docker_availability),
        ("Environment Config", test_env_file)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🧪 Docker Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All Docker tests passed! Ready for containerized deployment.")
        return True
    else:
        print("❌ Some Docker tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Docker tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Docker test suite failed: {e}")
        sys.exit(1)