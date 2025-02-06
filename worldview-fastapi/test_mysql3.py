#!/usr/bin/env python3
import logging
import uuid
from db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database():
    """Comprehensive database test"""
    db = DatabaseManager()
    
    try:
        # 1. Test basic connectivity
        logger.info("Testing basic connectivity...")
        result = db.test_connection()
        logger.info(f"Connection test result: {result}")

        # 2. Test write operation
        logger.info("\nTesting write operation...")
        test_data = {
            "session_id": str(uuid.uuid4()),
            "q1_response": 1,
            "q2_response": 2,
            "q3_response": 3,
            "q4_response": 4,
            "q5_response": 5,
            "q6_response": 6,
            "n1": 100,
            "n2": 200,
            "n3": 300,
            "plot_x": 123.45,
            "plot_y": 678.90,
            "browser": "Test Browser",
            "region": "Test Region",
            "source": "test",
            "hash_email_session": None
        }
        
        record_id = db.save_response(test_data)
        logger.info(f"Saved test record with ID: {record_id}")

        # 3. Test read operation
        logger.info("\nTesting read operation...")
        connection = db.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM survey_results WHERE id = %s", (record_id,))
        result = cursor.fetchone()
        logger.info(f"Retrieved test record: {result}")
        cursor.close()

        logger.info("\nAll tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

    finally:
        db.disconnect()

if __name__ == "__main__":
    try:
        success = test_database()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)