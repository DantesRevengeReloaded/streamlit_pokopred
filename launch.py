#!/usr/bin/env python3
"""
Quick launcher for the Football Predictions Dashboard.
Run this script to start the Streamlit app with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def detect_cloud_environment():
    """Detect if we're running in Streamlit Cloud."""
    cloud_indicators = [
        os.getenv('STREAMLIT_SHARING_MODE'),
        os.getenv('STREAMLIT_CLOUD'),
        'streamlit' in os.getenv('HOSTNAME', '').lower(),
        '/mount/src/' in str(Path.cwd()),  # Streamlit Cloud path pattern
        os.path.exists('/mount/src')
    ]
    return any(cloud_indicators)

def main():
    print("Football Predictions Dashboard Launcher")
    print("=" * 50)
    
    # Detect environment
    is_cloud = detect_cloud_environment()
    print(f"🌍 Running in: {'Streamlit Cloud' if is_cloud else 'Local Environment'}")
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check for .env file (only required for local, optional for cloud)
    env_file = Path(".env")
    if not is_cloud and not env_file.exists():
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure your database credentials")
        return 1
    elif env_file.exists():
        print("✅ Found .env file")
    elif is_cloud:
        print("☁️ Running in cloud - using cloud secrets")
    
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
        if not is_cloud:
            print("   Run: pip install -r requirements.txt")
        return 1
    
    # Test database connection (non-blocking for cloud)
    print("🗄️ Testing database connection...")
    try:
        sys.path.append('.')
        from db import test_database_connection
        
        if test_database_connection():
            print("✅ Database connection successful")
        else:
            if is_cloud:
                print("⚠️ Database connection failed - app will start anyway")
            else:
                print("❌ Database connection failed")
                print("   Please check your .env file credentials")
                return 1
    except Exception as e:
        if is_cloud:
            print(f"⚠️ Database test failed: {e} - app will start anyway")
        else:
            print(f"❌ Database test failed: {e}")
            return 1
    
    if is_cloud:
        # For Streamlit Cloud: Execute the app content directly
        print("🚀 Starting app for Streamlit Cloud...")
        try:
            # Import and execute the app module
            exec(open('app.py').read())
            return 0
        except Exception as e:
            print(f"❌ Failed to run app: {e}")
            return 1
    else:
        # For local development: Launch subprocess
        print("🚀 Launching Streamlit application locally...")
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
    if detect_cloud_environment():
        # In cloud, run the main function and then execute the app
        main()
    else:
        # In local, run normally
        sys.exit(main())