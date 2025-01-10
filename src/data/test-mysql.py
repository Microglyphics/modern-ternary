from src.config.database import DatabaseConfig
import mysql.connector
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

print("Python Path:", sys.path)

db_config = DatabaseConfig.get_db_config()

try:
    connection = mysql.connector.connect(**db_config)
    print("Connection successful!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")
