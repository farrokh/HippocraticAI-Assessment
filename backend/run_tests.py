#!/usr/bin/env python3
"""
Test runner script for the backend API.
Run this script to execute all tests.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests using pytest"""
    # Change to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Run pytest with verbose output using uv
    cmd = ["uv", "run", "pytest", "-v", "--tb=short"]
    
    print("Running backend tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("-" * 50)
        print("✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("-" * 50)
        print("❌ Some tests failed!")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install test dependencies:")
        print("pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
