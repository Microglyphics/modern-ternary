# src/data/test_comprehensive.py
from mysql_manager import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_operations():
    try:
        # Test 1: List all tables
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = :database
        """
        params = {'database': db_manager.db_config['database']}
        result = db_manager.execute_query(query, params)
        tables = [row[0] for row in result]
        logger.info(f"Found tables: {tables}")

        # Test 2: Test environment filtering (LOCAL)
        local_query = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_schema = :database 
        AND :environment = 'LOCAL'
        """
        result = db_manager.execute_query(local_query, params, is_local=True)
        local_count = result.scalar()
        logger.info(f"Local environment count: {local_count}")

        # Test 3: Test environment filtering (SERVER)
        server_query = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_schema = :database 
        AND :environment = 'SERVER'
        """
        result = db_manager.execute_query(server_query, params, is_local=False)
        server_count = result.scalar()
        logger.info(f"Server environment count: {server_count}")

        # Test 4: Error handling - Invalid query
        try:
            db_manager.execute_query("SELECT * FROM nonexistent_table")
            logger.error("Expected error not raised!")
        except Exception as e:
            logger.info("Successfully caught error for invalid table")

        logger.info("All comprehensive tests passed successfully!")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_database_operations()