#!/usr/bin/env python3
"""
Quick test and launch for the Football Dashboard
"""

print("🏈 Football Predictions Dashboard")
print("=" * 40)

try:
    # Test imports
    print("📦 Testing imports...")
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from dotenv import load_dotenv
    import os
    
    # Load environment variables
    load_dotenv()
    
    print("✅ All imports successful")
    
    # Test database connection
    print("🗄️ Testing database connection...")
    import sys
    sys.path.append('.')
    from db import test_database_connection
    
    if test_database_connection():
        print("✅ Database connection successful")
        
        print("\n🚀 Starting Streamlit application...")
        print("📱 Open your browser to: http://127.0.0.1:8501")
        print("⏹️  Press Ctrl+C to stop")
        print()
        
        import subprocess
        subprocess.run([
            "streamlit", "run", "app.py",
            "--server.port=8501", 
            "--server.address=127.0.0.1",
            "--browser.gatherUsageStats=false"
        ])
    else:
        print("❌ Database connection failed")
        print("   Check your .env file credentials")

except Exception as e:
    print(f"❌ Error: {e}")
    print("   Make sure all dependencies are installed: pip install -r requirements.txt")