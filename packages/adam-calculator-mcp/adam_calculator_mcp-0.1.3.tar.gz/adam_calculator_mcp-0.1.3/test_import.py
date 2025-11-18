#!/usr/bin/env python3
"""Test script to verify package import."""

try:
    import adam_calculator_mcp
    print("SUCCESS: Package imported successfully!")
    print(f"Package path: {adam_calculator_mcp.__file__}")
except ImportError as e:
    print(f"IMPORT FAILED: {e}")
except Exception as e:
    print(f"UNEXPECTED ERROR: {e}")
