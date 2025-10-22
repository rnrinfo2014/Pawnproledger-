"""
Diagnostic script to check import issues on Render
"""
import sys
import os
from pathlib import Path

print("=== DIAGNOSTIC INFORMATION ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")
print(f"Python path: {sys.path[:10]}")  # First 10 entries

# Check directory structure
current_dir = Path.cwd()
print(f"\nDirectory structure at {current_dir}:")
try:
    for item in current_dir.iterdir():
        if item.is_dir():
            print(f"  DIR:  {item.name}")
        else:
            print(f"  FILE: {item.name}")
except Exception as e:
    print(f"Error listing directory: {e}")

# Check if src directory exists and what's in it
src_dir = current_dir / "src"
print(f"\nChecking src directory at {src_dir}:")
if src_dir.exists():
    print("src directory exists!")
    try:
        for item in src_dir.iterdir():
            if item.is_dir():
                print(f"  DIR:  {item.name}")
            else:
                print(f"  FILE: {item.name}")
    except Exception as e:
        print(f"Error listing src directory: {e}")
else:
    print("src directory does NOT exist!")

# Check core directory
core_dir = src_dir / "core"
print(f"\nChecking core directory at {core_dir}:")
if core_dir.exists():
    print("core directory exists!")
    try:
        for item in core_dir.iterdir():
            if item.is_file() and item.name.endswith('.py'):
                print(f"  PY FILE: {item.name}")
    except Exception as e:
        print(f"Error listing core directory: {e}")
else:
    print("core directory does NOT exist!")

# Try imports step by step
print("\n=== IMPORT TESTING ===")

# Test 1: Basic FastAPI import
try:
    from fastapi import FastAPI
    print("✓ FastAPI import successful")
except ImportError as e:
    print(f"✗ FastAPI import failed: {e}")

# Test 2: Try to import config first
config_attempts = ["src.core.config", "core.config", "config"]
for attempt in config_attempts:
    try:
        print(f"Testing config import: {attempt}")
        module = __import__(attempt, fromlist=['settings'])
        settings = getattr(module, 'settings', None)
        if settings:
            print(f"✓ Config import successful from {attempt}")
            print(f"  Database URL present: {'DATABASE_URL' in os.environ or hasattr(settings, 'database_url')}")
            break
        else:
            print(f"✗ Config imported but no settings found in {attempt}")
    except ImportError as e:
        print(f"✗ Config import failed for {attempt}: {e}")
    except Exception as e:
        print(f"✗ Config import error for {attempt}: {e}")

# Test 3: Try to import main app
main_attempts = ["src.core.main", "core.main", "main"]
for attempt in main_attempts:
    try:
        print(f"Testing main app import: {attempt}")
        module = __import__(attempt, fromlist=['app'])
        app = getattr(module, 'app', None)
        if app:
            print(f"✓ Main app import successful from {attempt}")
            print(f"  App type: {type(app)}")
            # Try to get routes
            try:
                routes = getattr(app, 'routes', [])
                print(f"  Number of routes: {len(routes)}")
            except:
                print("  Could not get route count")
            break
        else:
            print(f"✗ Main imported but no app found in {attempt}")
    except ImportError as e:
        print(f"✗ Main app import failed for {attempt}: {e}")
    except Exception as e:
        print(f"✗ Main app import error for {attempt}: {e}")

print("\n=== END DIAGNOSTIC ===")