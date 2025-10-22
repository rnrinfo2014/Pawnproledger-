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

# For Render deployment, also add the current directory to path
current_dir = Path.cwd()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

# Also add parent directories that might contain the src folder
parent_src = current_dir.parent / "src"
if parent_src.exists():
    sys.path.insert(0, str(parent_src))
    sys.path.insert(0, str(current_dir.parent))

print(f"Current working directory: {current_dir}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:5]}")  # Print first 5 entries

# Import and run the application
if __name__ == "__main__":
    import uvicorn
    
    # Try different app module paths for different deployment environments
    config_found = False
    app_module = None
    
    # Try multiple import strategies
    import_attempts = [
        ("src.core.config", "src.core.main:app"),
        ("core.config", "core.main:app"),
        ("config", "main:app"),
    ]
    
    for config_import, app_import in import_attempts:
        try:
            print(f"[RUN_SERVER] Attempting config import: {config_import}")
            module = __import__(config_import, fromlist=['settings'])
            settings = module.settings
            app_module = app_import
            config_found = True
            print(f"[RUN_SERVER] Successfully imported config from: {config_import}")
            print(f"[RUN_SERVER] Will use app module: {app_import}")
            break
        except ImportError as e:
            print(f"[RUN_SERVER] Failed to import {config_import}: {e}")
            continue
    
    if not config_found:
        # Fallback to environment variables
        print("Using fallback environment configuration")
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        log_level = os.getenv("LOG_LEVEL", "info")
        environment = os.getenv("ENVIRONMENT", "production")
        
        # Try to find the main app
        main_attempts = ["src.core.main:app", "core.main:app", "main:app"]
        app_module = None
        
        for attempt in main_attempts:
            try:
                module_path, app_name = attempt.split(":")
                __import__(module_path)
                app_module = attempt
                print(f"Successfully found app at: {attempt}")
                break
            except ImportError as e:
                print(f"Failed to import {attempt}: {e}")
                continue
        
        if not app_module:
            raise RuntimeError("Could not find the FastAPI app module")
    else:
        host = settings.host
        port = settings.port
        log_level = settings.log_level.lower()
        environment = settings.environment
    
    if not app_module:
        raise RuntimeError("Could not find the FastAPI app module")
        
    print(f"Starting server with app: {app_module}")
    print(f"Host: {host}, Port: {port}, Environment: {environment}")
    
    # Run the application
    uvicorn.run(
        app_module,
        host=host,
        port=port,
        reload=True if environment == "development" else False,
        log_level=log_level
    )