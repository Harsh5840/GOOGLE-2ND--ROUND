#!/usr/bin/env python3
"""
Script to install missing dependencies for the news podcast agent.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_package(package):
    """Check if a package is installed."""
    try:
        __import__(package)
        print(f"✅ {package} is already installed")
        return True
    except ImportError:
        print(f"❌ {package} is not installed")
        return False

def main():
    """Main function to install dependencies."""
    print("=== Installing Missing Dependencies ===\n")
    
    # List of required packages
    required_packages = [
        "google-generativeai",
        "python-dotenv",
        "newsapi-python",
        "google-cloud-texttospeech"
    ]
    
    # Check and install packages
    for package in required_packages:
        if not check_package(package.replace("-", "_")):
            install_package(package)
        print()
    
    print("=== Installation Complete ===")
    print("\nYou can now run:")
    print("  python test_tools.py")
    print("  python run_simple.py")

if __name__ == "__main__":
    main() 