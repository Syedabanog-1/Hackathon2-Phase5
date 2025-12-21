"""
Vercel entrypoint for the FastAPI application.
This file exports the FastAPI app for Vercel serverless deployment.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app from the main chatbot CLI
from src.cli.chatbot_cli import app

# Export the app for Vercel
# Vercel looks for 'app' variable in this file
__all__ = ['app']
