#!/usr/bin/env python3
"""
Quick launcher for the Football Predictions Dashboard.
Run this script to start the Streamlit app with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("Football Predictions Dashboard Launcher")
    print("=" * 50)
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure your database credentials")
        return 1
    
    print("✅ Found .env file")
    
    # Check required packages
    try:
        import streamlit
        import psycopg2
        import plotly
        import pandas
        from dotenv import load_dotenv
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Run: pip install -r requirements.txt")
        return 1
    
    # Test database connection
    print("🗄️ Testing database connection...")
    try:
        sys.path.append('.')
        from db import test_database_connection
        
        if test_database_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            print("   Please check your .env file credentials")
            return 1
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return 1
    
    # Launch Streamlit
    print("🚀 Launching Streamlit application...")
    print("   📱 Open your browser to: http://localhost:8501")
    print("   ⏹️  Press Ctrl+C to stop the application")
    print()
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
        return result.returncode
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Failed to launch Streamlit: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())