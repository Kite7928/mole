"""
Vercel Serverless Function entry point for FastAPI backend.
This file enables FastAPI to run on Vercel's serverless platform.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from app.main import app

# Handle Vercel's request/response format
from mangum import Mangum

# Create ASGI handler for Vercel
handler = Mangum(app)

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)