# src/scripts/initialise_mysql_db.py
import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the MySQL database and create required tables"""
    
    # Configuration for initial connection (without database)
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'iva9Bry$'  # Replace with your MySQL root password
    }
    
    try:
        # First, connect without database to create it if needed
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS modernity_survey")
        logger.info("Database 'modernity_survey' created or already exists")
        
        # Switch to the database
        cursor.execute("USE modernity_survey")
        
        # Create responses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            responses JSON NOT NULL,
            scores JSON NOT NULL,
            aggregate_response JSON NOT NULL,
            INDEX idx_timestamp (timestamp)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        logger.info("Table 'responses' created or already exists")
        
        # Create survey_results table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_results (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            q1_response INT,
            q2_response INT,
            q3_response INT,
            q4_response INT,
            q5_response INT,
            q6_response INT,
            n1 INT,
            n2 INT,
            n3 INT,
            plot_x DECIMAL(10,2),
            plot_y DECIMAL(10,2),
            session_id VARCHAR(255),
            hash_email_session VARCHAR(255),
            browser VARCHAR(255) DEFAULT NULL,
            region VARCHAR(50) DEFAULT NULL,
            source VARCHAR(50) DEFAULT 'local',
            INDEX idx_timestamp (timestamp),
            INDEX idx_session (session_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        logger.info("Table 'survey_results' created or already exists")
        
        conn.commit()
        logger.info("Database initialization completed successfully")
        
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    initialize_database()