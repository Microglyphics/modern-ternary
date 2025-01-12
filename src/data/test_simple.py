# src/data/test_simple.py
from mysql_manager import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_connection():
    try:
        # Test 1: Simple table count
        query = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_schema = :database
        """
        params = {'database': db_manager.db_config['database']}
        
        result = db_manager.execute_query(query, params)
        count = result.scalar()
        logger.info(f"Found {count} tables in database")

        if count == 2:  # Matching what we just saw in MySQL shell
            logger.info("Database connection and query successful!")
        else:
            logger.warning(f"Unexpected table count: {count}")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_basic_connection()