#!/usr/bin/env python3
"""
Quick launcher for the Football Predictions Dashboard.
Run this script to start the Streamlit app with proper environment setup.
"""

import os
import sys
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

    is_cloud = detect_cloud_environment()
    print(f"🌍 Running in: {'Streamlit Cloud' if is_cloud else 'Local Environment'}")

    if not is_cloud:
        print("❌ This launcher is intended for Streamlit Cloud deployments only.")
        print("   Please use `streamlit run app.py` for local development.")
        return 1

    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print("☁️ Running in cloud - using Streamlit Cloud secrets")
    print("   💡 Configure credentials in Streamlit Cloud dashboard under Settings → Secrets")

    try:
        import streamlit  # noqa: F401
        import psycopg2  # noqa: F401
        import plotly  # noqa: F401
        import pandas  # noqa: F401
        from dotenv import load_dotenv  # noqa: F401
        print("✅ All required packages are available")
    except ImportError as err:
        print(f"❌ Missing package: {err}")
        return 1

    print("🗄️ Testing database connection...")
    try:
        sys.path.append('.')
        from db import test_database_connection

        if test_database_connection():
            print("✅ Database connection successful")
        else:
            print("⚠️ Database connection failed - app will start anyway")
    except Exception as err:
        print(f"⚠️ Database test failed: {err} - app will start anyway")

    print("🚀 Starting app for Streamlit Cloud...")
    try:
        import streamlit as st
        import pandas as pd
        import numpy as np
        import plotly.express as px
        import plotly.graph_objects as go
        from datetime import datetime, date, timedelta
        import warnings

        warnings.filterwarnings('ignore')

        import db
        import geo

        app_globals = {
            'st': st,
            'pd': pd,
            'np': np,
            'px': px,
            'go': go,
            'datetime': datetime,
            'date': date,
            'timedelta': timedelta,
            'warnings': warnings,
            'db': db,
            'geo': geo,
            '__name__': '__main__'
        }

        with open('app.py', 'r', encoding='utf-8') as app_file:
            app_code = app_file.read()
        exec(app_code, app_globals)
        return 0
    except Exception as err:
        print(f"❌ Failed to run app: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())