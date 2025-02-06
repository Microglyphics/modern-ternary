# test_mysql.py
import mysql.connector
import os
import time
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cloud_sql():
    """Test direct connection to Cloud SQL"""
    logger.info("Testing Cloud SQL connection...")
    
    # Connection configs to test
    configs = [
        {
            "name": "Unix Socket",
            "config": {
                'user': 'app_user',
                'password': '9pQK?fJF.9Lm]nv;',
                'database': 'modernity_survey',
                'unix_socket': '/cloudsql/modernity-worldview:us-central1:modernity-worldview-db'
            }
        },
        {
            "name": "TCP Connection",
            "config": {
                'user': 'app_user',
                'password': '9pQK?fJF.9Lm]nv;',
                'database': 'modernity_survey',
                'host': '127.0.0.1',
                'port': 3307
            }
        }
    ]

    for test in configs:
        logger.info(f"\nTesting {test['name']}:")
        logger.info(f"Connection parameters: {test['config']}")
        
        try:
            start_time = time.time()
            conn = mysql.connector.connect(**test['config'])
            
            if conn.is_connected():
                db_info = conn.get_server_info()
                cursor = conn.cursor()
                cursor.execute("SELECT DATABASE();")
                db_name = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM survey_results;")
                count = cursor.fetchone()[0]
                
                logger.info(f"Success! Connected to MySQL Server version {db_info}")
                logger.info(f"Connected to database: {db_name}")
                logger.info(f"Survey results count: {count}")
                logger.info(f"Connection time: {time.time() - start_time:.2f} seconds")
                
            conn.close()
            logger.info("MySQL connection closed successfully")
            
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            if 'conn' in locals() and conn.is_connected():
                conn.close()
                logger.info("MySQL connection closed")

if __name__ == "__main__":
    test_cloud_sql()