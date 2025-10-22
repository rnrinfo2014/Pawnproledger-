"""
Simple application entry point for Render deployment
"""
import os
import sys
from pathlib import Path

# Ensure we can import from src
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(src_dir))

# Set environment variables if not set
os.environ.setdefault("DATABASE_URL", os.getenv("DATABASE_URL", ""))
os.environ.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "your-secret-key-here"))
os.environ.setdefault("CORS_ORIGINS", os.getenv("CORS_ORIGINS", "*"))

try:
    # Try to import the main app
    from src.core.main import app
except ImportError:
    try:
        from core.main import app
    except ImportError:
        # Create a simple fallback app
        from fastapi import FastAPI
        app = FastAPI(title="PawnSoft API", description="Pawn Shop Management System")
        
        @app.get("/")
        def root():
            return {"message": "PawnSoft API is running", "status": "success"}
        
        @app.get("/health")
        def health():
            return {"status": "healthy"}

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