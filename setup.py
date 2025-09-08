#!/usr/bin/env python3
"""
Setup script for Quantum-Enhanced AI Logistics Engine
D3CODE 2025 Hackathon Project
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Please use Python 3.8 or higher")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✅ Node.js {version} found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found")
        print("   Please install Node.js from https://nodejs.org/")
        return False

def setup_python_environment():
    """Set up Python environment and dependencies"""
    print("\n🐍 Setting up Python environment...")
    
    # Create virtual environment
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
    else:
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"
    
    # Install Python dependencies
    if not run_command(f"{pip_command} install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{pip_command} install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    print("✅ Python environment ready")
    return True

def setup_node_environment():
    """Set up Node.js environment and dependencies"""
    print("\n🌐 Setting up Node.js environment...")
    
    if not run_command("npm install", "Installing Node.js dependencies"):
        return False
    
    print("✅ Node.js environment ready")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ['public', 'logs', 'data']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")
    
    return True

def run_tests():
    """Run basic tests to verify installation"""
    print("\n🧪 Running tests...")
    
    # Test Python imports
    try:
        import numpy, scipy, pandas, sklearn, flask, dimod
        print("✅ Python dependencies test passed")
    except ImportError as e:
        print(f"❌ Python dependencies test failed: {e}")
        return False
    
    # Test Node.js dependencies
    if not os.path.exists('node_modules'):
        print("❌ Node.js dependencies not found")
        return False
    else:
        print("✅ Node.js dependencies test passed")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Quantum-Enhanced AI Logistics Engine Setup")
    print("=" * 60)
    print("D3CODE 2025 Hackathon Project")
    print("AI + Quantum + Data Ecosystems")
    print("=" * 60)
    
    # Check system requirements
    if not check_python_version():
        return False
    
    if not check_node_version():
        return False
    
    # Set up environments
    if not setup_python_environment():
        return False
    
    if not setup_node_environment():
        return False
    
    if not create_directories():
        return False
    
    if not run_tests():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("=" * 60)
    print("Next steps:")
    print("1. Run: python start.py")
    print("2. Open: http://localhost:3000")
    print("3. Or run demo: python demo.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
