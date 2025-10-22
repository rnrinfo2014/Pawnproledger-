"""
Simple application entry point for Render deployment
"""
import os
import sys
from pathlib import Path

# First run diagnostics
print("=== STARTING RENDER DIAGNOSTICS ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")

# Ensure we can import from src - comprehensive path setup
current_dir = Path(__file__).parent
src_dir = current_dir / "src"

# For Render deployment, also add the current directory to path
current_working_dir = Path.cwd()
sys.path.insert(0, str(current_working_dir))
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(src_dir))

# Also add parent directories that might contain the src folder
parent_src = current_working_dir.parent / "src"
if parent_src.exists():
    sys.path.insert(0, str(parent_src))
    sys.path.insert(0, str(current_working_dir.parent))

print(f"[APP] Current working directory: {current_working_dir}")
print(f"[APP] App file directory: {current_dir}")
print(f"[APP] Python path entries: {sys.path[:5]}")

# Check directory structure
print(f"\n[APP] Directory structure at {current_working_dir}:")
try:
    items = list(current_working_dir.iterdir())[:10]  # First 10 items
    for item in items:
        if item.is_dir():
            print(f"  DIR:  {item.name}")
        else:
            print(f"  FILE: {item.name}")
except Exception as e:
    print(f"[APP] Error listing directory: {e}")

# Check if src directory exists
print(f"\n[APP] Checking src directory at {src_dir}:")
if src_dir.exists():
    print("[APP] src directory exists!")
    try:
        items = list(src_dir.iterdir())
        for item in items:
            if item.is_dir():
                print(f"  DIR:  {item.name}")
    except Exception as e:
        print(f"[APP] Error listing src directory: {e}")
else:
    print("[APP] src directory does NOT exist!")

# Set environment variables if not set
os.environ.setdefault("DATABASE_URL", os.getenv("DATABASE_URL", ""))
os.environ.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "your-secret-key-here"))
os.environ.setdefault("CORS_ORIGINS", os.getenv("CORS_ORIGINS", "*"))

# Try multiple import strategies for the main app
app = None
import_attempts = [
    "core.main",        # This should work since we're in /opt/render/project/src
    "src.core.main",    # Fallback for local development
    "main"              # Last resort
]

for import_path in import_attempts:
    try:
        print(f"[APP] Attempting to import app from: {import_path}")
        module = __import__(f"{import_path}", fromlist=['app'])
        app = module.app
        print(f"[APP] Successfully imported app from: {import_path}")
        print(f"[APP] App type: {type(app)}")
        # Check if app has routes
        try:
            routes = getattr(app, 'routes', [])
            print(f"[APP] Number of routes found: {len(routes)}")
        except:
            print("[APP] Could not count routes")
        break
    except ImportError as e:
        print(f"[APP] Failed to import {import_path}: {e}")
        continue
    except Exception as e:
        print(f"[APP] Unexpected error importing {import_path}: {e}")
        continue

# If all imports failed, create a fallback app
if app is None:
    print("[APP] All imports failed, creating fallback app")
    from fastapi import FastAPI
    app = FastAPI(title="PawnSoft API - Fallback", description="Pawn Shop Management System - Fallback Mode")
    
    @app.get("/")
    def root():
        return {
            "message": "PawnSoft API is running in fallback mode", 
            "status": "fallback", 
            "note": "Main app could not be imported",
            "cwd": str(Path.cwd()),
            "paths_tried": import_attempts
        }
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "mode": "fallback"}
    
    @app.get("/debug")
    def debug():
        return {
            "cwd": str(Path.cwd()),
            "python_path": sys.path[:10],
            "env_vars": {k:v for k, v in os.environ.items() if 'DATABASE' in k or 'SECRET' in k or 'CORS' in k}
        }
else:
    print("[APP] Successfully loaded main application with all routes!")

print("=== END RENDER DIAGNOSTICS ===\n")

# This is what Render will use
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False
    )