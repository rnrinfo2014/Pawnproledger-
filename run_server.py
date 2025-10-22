#!/usr/bin/env python3
"""
PawnSoft Application Startup Script
This script ensures the application starts with correct paths and imports
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the application
if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "src.core.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "src")]
    )