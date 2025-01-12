# src/data/test_db.py
from mysql_manager import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    try:
        # Test 1: Basic Connection
        with db_manager.get_session() as session:
            result = session.execute("SELECT 1").scalar()
            assert result == 1
            logger.info("Basic connection test passed")

        # Test 2: Environment Filtering (LOCAL)
        query = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_schema = :database
        """
        params = {'database': db_manager.db_config['database']}
        
        result = db_manager.execute_query(query, params, is_local=True)
        local_count = result.scalar()
        logger.info(f"Found {local_count} tables in database (LOCAL environment)")

        # Test 3: Environment Filtering (SERVER)
        result = db_manager.execute_query(query, params, is_local=False)
        server_count = result.scalar()
        logger.info(f"Found {server_count} tables in database (SERVER environment)")

        logger.info("All database tests passed successfully!")

    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_database()