"""
Simple application entry point for Render deployment
"""
import os
import sys
from pathlib import Path

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

# Set environment variables if not set
os.environ.setdefault("DATABASE_URL", os.getenv("DATABASE_URL", ""))
os.environ.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "your-secret-key-here"))
os.environ.setdefault("CORS_ORIGINS", os.getenv("CORS_ORIGINS", "*"))

# Try multiple import strategies for the main app
app = None
import_attempts = [
    "src.core.main",
    "core.main",
    "main"
]

for import_path in import_attempts:
    try:
        print(f"[APP] Attempting to import app from: {import_path}")
        module = __import__(f"{import_path}", fromlist=['app'])
        app = module.app
        print(f"[APP] Successfully imported app from: {import_path}")
        break
    except ImportError as e:
        print(f"[APP] Failed to import {import_path}: {e}")
        continue

# If all imports failed, create a fallback app
if app is None:
    print("[APP] All imports failed, creating fallback app")
    from fastapi import FastAPI
    app = FastAPI(title="PawnSoft API - Fallback", description="Pawn Shop Management System - Fallback Mode")
    
    @app.get("/")
    def root():
        return {"message": "PawnSoft API is running in fallback mode", "status": "fallback", "note": "Main app could not be imported"}
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "mode": "fallback"}

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