# src/config/database.py
import os
from typing import Dict

class DatabaseConfig:
    @staticmethod
    def get_db_config() -> Dict[str, str]:
        """Get database configuration from environment variables"""
        return {
            'host': os.getenv('DB_HOST', '35.222.251.0'),
            'user': os.getenv('DB_USER', 'app_user'),
            'password': os.getenv('DB_PASSWORD', ''),  # Set in environment
            'database': os.getenv('DB_NAME', 'modernity_survey'),
            'port': int(os.getenv('DB_PORT', '3306'))
        }