#!/usr/bin/env python3
"""
Configuration settings and environment setup for the Football Predictions Dashboard.
"""

import os
import json
from typing import Dict, Any, Optional

# Default configuration values
DEFAULT_CONFIG = {
    'database': {
        'host': 'localhost',
        'port': 5432,
        'database': 'football_predictions',
        'user': 'postgres',
        'password': 'password'
    },
    'app': {
        'title': 'Football Predictions Dashboard',
        'page_icon': 'images/pokopred_logo.png',
        'layout': 'wide',
        'cache_ttl': 300,  # 5 minutes
        'max_rows_display': 100
    },
    'maps': {
        'default_style': 'dark',
        'default_zoom': 5,
        'center_lat': 50.0,
        'center_lon': 10.0
    }
}

class AppConfig:
    """Application configuration manager."""
    
    def __init__(self, config_path: str = "../config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment variables."""
        config = DEFAULT_CONFIG.copy()
        
        # Try to load from config file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Override with environment variables if present
        env_overrides = {
            'database': {
                'host': os.getenv('DB_HOST'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'database': os.getenv('DB_NAME'),
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD')
            }
        }
        
        # Apply non-None environment overrides
        for section, settings in env_overrides.items():
            if section not in config:
                config[section] = {}
            for key, value in settings.items():
                if value is not None:
                    config[section][key] = value
        
        return config
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(section, {}).get(key, default)
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.config.get('database', {})
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return self.config.get('app', {})
    
    def get_map_config(self) -> Dict[str, Any]:
        """Get map configuration."""
        return self.config.get('maps', {})

# Global configuration instance
app_config = AppConfig()