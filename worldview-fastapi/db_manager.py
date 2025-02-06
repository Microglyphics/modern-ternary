import os
import time
import mysql.connector
from mysql.connector import Error, pooling
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        logger.info("Initializing DatabaseManager")
        self.is_gae = os.getenv('GAE_ENV', '').startswith('standard')
        logger.info(f"Running in App Engine: {self.is_gae}")
        self._config = self._get_db_config()
        logger.info(f"Database config (sanitized): {self._sanitize_config(self._config)}")
        
        # Initialize connection pool
        self.pool_config = {
            'pool_name': 'mypool',
            'pool_size': 5,
            'pool_reset_session': True,
            **self._config
        }
        
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.pool_config)
            logger.info("Connection pool created successfully")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    def _sanitize_config(self, config):
        """Remove sensitive info for logging"""
        safe_config = config.copy()
        if 'password' in safe_config:
            safe_config['password'] = '***'
        return safe_config

    def _get_db_config(self):
        """Get database configuration based on environment"""
        if self.is_gae:
            # App Engine - use Unix socket with correct instance name
            instance_name = os.getenv('INSTANCE_CONNECTION_NAME', 
                                    'modernity-worldview:us-central1:modernity-db')
            logger.info(f"Using Cloud SQL instance: {instance_name}")
            
            socket_path = f"/cloudsql/{instance_name}"
            logger.info(f"Socket path: {socket_path}")
            
            return {
                'user': os.getenv('DB_USER', 'app_user'),
                'password': os.getenv('DB_PASSWORD', '9pQK?fJF.9Lm]nv;'),
                'database': os.getenv('DB_NAME', 'modernity_survey'),
                'unix_socket': socket_path,
                'connect_timeout': 60  # Increase timeout for cloud connections
            }
        else:
            # Local development - use TCP with Cloud SQL proxy
            logger.info("Using local development configuration")
            return {
                'host': os.getenv('DB_HOST', '127.0.0.1'),
                'port': int(os.getenv('DB_PORT', '3307')),
                'user': os.getenv('DB_USER', 'app_user'),
                'password': os.getenv('DB_PASSWORD', '9pQK?fJF.9Lm]nv;'),
                'database': os.getenv('DB_NAME', 'modernity_survey'),
                'connect_timeout': 10  # Shorter timeout for local connections
            }

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool with context management"""
        connection = None
        try:
            connection = self.pool.get_connection()
            logger.info("Got connection from pool")
            yield connection
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise
        finally:
            if connection:
                connection.close()
                logger.info("Connection returned to pool")

    def save_response(self, survey_data: dict) -> int:
        """Save survey response with retries"""
        max_attempts = 3
        last_error = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Save attempt {attempt}/{max_attempts}")
                
                with self.get_connection() as connection:
                    cursor = connection.cursor()
                    
                    query = """INSERT INTO survey_results 
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
                    connection.commit()
                    
                    record_id = cursor.lastrowid
                    logger.info(f"Successfully saved survey response with ID: {record_id}")
                    cursor.close()
                    return record_id

            except Error as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < max_attempts:
                    logger.info("Retrying in 2 seconds...")
                    time.sleep(2)
                continue

        raise RuntimeError(f"Failed to save survey after {max_attempts} attempts: {last_error}")

    def test_connection(self):
        """Test database connectivity"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Test queries
                cursor.execute("SELECT COUNT(*) FROM survey_results")
                count = cursor.fetchone()[0]
                
                # Get connection type
                conn_type = "unix_socket" if "unix_socket" in self._config else "tcp"
                
                cursor.close()
                
                return {
                    "status": "success",
                    "record_count": count,
                    "connection_type": conn_type,
                    "config": {
                        k: v for k, v in self._config.items() 
                        if k not in ['password']
                    }
                }
                
        except Error as e:
            return {
                "status": "error",
                "message": str(e),
                "config": self._sanitize_config(self._config)
            }

    def __del__(self):
        """Cleanup connection pool on destruction"""
        # The pool will automatically close all connections