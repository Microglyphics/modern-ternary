# db_manager.py
import os
import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            if os.getenv('GAE_ENV', '').startswith('standard'):
                # Production configuration
                config = {
                    'unix_socket': '/cloudsql/modernity-worldview:us-central1:modernity-db',
                    'user': 'app_user',
                    'password': '9pQK?fJF.9Lm]nv;',
                    'database': 'modernity_survey'
                }
            else:
                # Development configuration
                config = {
                    'host': '127.0.0.1',
                    'user': 'app_user',
                    'password': '9pQK?fJF.9Lm]nv;',
                    'database': 'modernity_survey',
                    'port': 3307
                }
            
            self.connection = mysql.connector.connect(**config)
            logging.info("Database connection successful")
        except Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def save_response(self, survey_data: dict) -> int:
        try:
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