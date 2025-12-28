#!/usr/bin/env python3
"""
Cloud entry point for the Football Predictions Dashboard.
This file is optimized for Streamlit Cloud deployment.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup environment for cloud deployment"""
    print("🌐 Setting up Football Predictions Dashboard for Streamlit Cloud")
    print("=" * 60)
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check required packages
    try:
        import streamlit
        import pandas
        import plotly
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        # In cloud, packages should be installed via requirements.txt
        return False
    
    # For cloud deployment, we don't test database here
    # Database credentials should be in Streamlit Cloud secrets
    print("✅ Environment setup complete")
    return True

# Run setup when imported
if __name__ == "__main__" or setup_environment():
    # Import the main app
    import app