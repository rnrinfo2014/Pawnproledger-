#!/usr/bin/env python3
"""
PawnSoft Application Startup Script
This script ensures the application starts with correct paths and imports
"""

import sys
import os
from pathlib import Path

# Add the project root and src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

# Import and run the application
if __name__ == "__main__":
    import uvicorn
    
    # Try different app module paths for different deployment environments
    try:
        from src.core.config import settings
        app_module = "src.core.main:app"
    except ImportError:
        from core.config import settings
        app_module = "core.main:app"
    
    # Run the application
    uvicorn.run(
        app_module,
        host=settings.host,
        port=settings.port,
        reload=True if settings.environment == "development" else False,
        reload_dirs=[str(project_root / "src")],
        log_level=settings.log_level.lower()
    )