# db_manager.py
import mysql.connector
import os
from mysql.connector import Error
import logging

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

    def save_response(self, response: dict):
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO survey_responses 
            (session_id, source, browser, q1_response, q2_response, q3_response, 
             q4_response, q5_response, q6_response, n1, n2, n3, plot_x, plot_y)
            VALUES (%(session_id)s, %(source)s, %(browser)s, %(q1_response)s, 
                    %(q2_response)s, %(q3_response)s, %(q4_response)s, %(q5_response)s, 
                    %(q6_response)s, %(n1)s, %(n2)s, %(n3)s, %(plot_x)s, %(plot_y)s)
            """
            cursor.execute(query, response)
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            logging.error(f"Error saving response: {e}")
            raise
        finally:
            cursor.close()