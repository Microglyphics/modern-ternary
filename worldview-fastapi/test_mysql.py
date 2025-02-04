import mysql.connector
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mysql_connection():
    """Test MySQL connection and write a funny record to the database."""
    logger.info("Testing MySQL connection...")
    
    try:
        logger.info("Connecting to MySQL...")
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='app_user',
            password='9pQK?fJF.9Lm]nv;',
            database='modernity_survey',
            port=3307
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"Connected to MySQL Server version {db_info}")

            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            logger.info(f"Connected to database: {record[0]}")

            # Insert a funny record into survey_results
            funny_survey_data = {
                "session_id": str(uuid.uuid4()),
                "q1_response": 1,
                "q2_response": 2,
                "q3_response": 3,
                "q4_response": 4,
                "q5_response": 5,
                "q6_response": 6,
                "n1": 42,
                "n2": 69,
                "n3": 420,
                "plot_x": 3.14,
                "plot_y": 2.71,
                "browser": "FunnyBrowser 9000",
                "region": "JokeRegion",
                "source": "comedy",
                "hash_email_session": "f00b4r-hash"
            }

            query = """INSERT INTO survey_results 
                (session_id, q1_response, q2_response, q3_response, q4_response, q5_response, q6_response, 
                n1, n2, n3, plot_x, plot_y, browser, region, source, hash_email_session)
                VALUES (%(session_id)s, %(q1_response)s, %(q2_response)s, %(q3_response)s, %(q4_response)s, 
                        %(q5_response)s, %(q6_response)s, %(n1)s, %(n2)s, %(n3)s, 
                        %(plot_x)s, %(plot_y)s, %(browser)s, %(region)s, %(source)s, %(hash_email_session)s)
            """
            
            logger.info("Inserting funny survey record...")
            cursor.execute(query, funny_survey_data)
            connection.commit()
            logger.info(f"Funny survey record inserted with ID: {cursor.lastrowid}")

    except mysql.connector.Error as e:
        logger.error(f"Error during MySQL operation: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            logger.info("MySQL connection closed.")

if __name__ == "__main__":
    test_mysql_connection()
