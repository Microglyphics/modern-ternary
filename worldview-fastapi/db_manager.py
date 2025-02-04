# db_manager.py
import os
import time
import json
import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        logger.info("Initializing DatabaseManager")

    def get_connection(self):
        """Get a fresh connection each time."""
        return mysql.connector.connect(
            host='127.0.0.1',
            user='app_user',
            password='9pQK?fJF.9Lm]nv;',
            database='modernity_survey',
            port=3307,
            connection_timeout=60  # Prevents timeout drops
        )

    def save_response(self, survey_data: dict) -> int:
        """Save survey response with retries to handle connection issues."""
        connection = None
        cursor = None
        max_attempts = 3  # Limit retries to avoid infinite loops

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Attempt {attempt}/{max_attempts}: Getting fresh database connection...")
                connection = self.get_connection()
                logger.info("Database connection established.")

                cursor = connection.cursor()
                logger.info("Cursor created.")

                query = """INSERT INTO survey_results 
                    (session_id, q1_response, q2_response, q3_response, q4_response, q5_response, q6_response, 
                    n1, n2, n3, plot_x, plot_y, browser, region, source, hash_email_session)
                    VALUES (%(session_id)s, %(q1_response)s, %(q2_response)s, %(q3_response)s, %(q4_response)s, 
                            %(q5_response)s, %(q6_response)s, %(n1)s, %(n2)s, %(n3)s, 
                            %(plot_x)s, %(plot_y)s, %(browser)s, %(region)s, %(source)s, %(hash_email_session)s)
                """

                logger.info(f"Executing query:\n{query}")
                logger.info(f"With parameters:\n{survey_data}")
                logger.info(f"Final values before insert: plot_x={survey_data.get('plot_x')}, plot_y={survey_data.get('plot_y')}")
                cursor.execute(query, survey_data)
                connection.commit()
                logger.info("Transaction committed.")

                last_id = cursor.lastrowid
                logger.info(f"Insert successful, last inserted ID: {last_id}")
                return last_id

            except mysql.connector.errors.OperationalError as e:
                logger.error(f"MySQL Connection lost: {e}. Retrying in 2 seconds...")
                time.sleep(2)  # Short delay before retry
            except mysql.connector.Error as e:
                logger.error(f"MySQL Execution Error: {e}")
                break  # Do not retry non-connection errors
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

        # 🚨 Move RuntimeError inside the function so FastAPI doesn't crash at startup
        raise RuntimeError("Failed to save survey response after multiple attempts")

    def test_connection(self):
        """Basic connection test."""
        logger.info("Testing database connection")
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM survey_results")
            count = cursor.fetchone()[0]
            logger.info(f"Current record count: {count}")
            return {"status": "success", "record_count": count}
        except Error as e:
            logger.error(f"Connection test failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
