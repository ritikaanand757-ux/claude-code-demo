#!/usr/bin/env python
"""Script to run tests and capture output"""
import subprocess
import sys

# Run pytest with verbose output
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_enhanced_api.py", "-v", "--tb=short"],
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")
