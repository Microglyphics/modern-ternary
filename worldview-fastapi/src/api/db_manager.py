# src/api/db_manager.py
import os
import mysql.connector
from mysql.connector import Error
import logging
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_config() -> Dict[str, Any]:
    """Get database configuration based on environment"""
    
    if os.getenv('GAE_ENV', '').startswith('standard'):
        # Production on App Engine
        connection_name = os.getenv("INSTANCE_CONNECTION_NAME", "modernity-worldview:us-central1:modernity-db")
        db_socket_dir = os.getenv("DB_SOCKET_DIR", "/cloudsql")
        
        return {
            'unix_socket': f'{db_socket_dir}/{connection_name}',
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'raise_on_warnings': True,
            'ssl_disabled': True  # Disable SSL since we're using Unix socket
        }
    else:
        # Local development
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'port': int(os.getenv('DB_PORT', 3307)),
            'raise_on_warnings': True
        }

class DatabaseManager:
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            config = get_db_config()
            logger.info(f"Attempting connection with config: {config}")
            self.connection = mysql.connector.connect(**config)
            logger.info("Database connection successful")
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def save_response(self, survey_data: dict) -> int:
        """Save survey response to database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            query = """
            INSERT INTO survey_results 
            (session_id, q1_response, q2_response, q3_response, q4_response, 
            q5_response, q6_response, n1, n2, n3, plot_x, plot_y, 
            browser, region, source, hash_email_session)
            VALUES (%(session_id)s, %(q1_response)s, %(q2_response)s, 
                    %(q3_response)s, %(q4_response)s, %(q5_response)s, 
                    %(q6_response)s, %(n1)s, %(n2)s, %(n3)s, %(plot_x)s, 
                    %(plot_y)s, %(browser)s, %(region)s, %(source)s, 
                    %(hash_email_session)s)
            """
            cursor.execute(query, survey_data)
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error saving response: {e}")
            raise
        finally:
            cursor.close()
            
    def __del__(self):
        """Close database connection on cleanup"""
        if self.connection and self.connection.is_connected():
            self.connection.close()