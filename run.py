#!/usr/bin/env python3
"""
Deployment script for the NBA Advanced Stats web application.
Run with: python run.py
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    # For production deployment, set debug=False
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🏀 Starting NBA Advanced Stats App")
    print(f"🌐 Running on http://0.0.0.0:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"📊 VIBE formula: Position-based defensive evaluation")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )