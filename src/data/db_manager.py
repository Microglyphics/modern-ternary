import os
import sqlite3
from typing import List, Optional

DB_PATH = "src/data/survey_results.db"

# Initialize the database schema if it doesn't exist
def initialize_database():
    if not os.path.exists(DB_PATH):  # Check if the database file exists
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE survey_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                q1_response INTEGER,
                q2_response INTEGER,
                q3_response INTEGER,
                q4_response INTEGER,
                q5_response INTEGER,
                q6_response INTEGER,
                n1 INTEGER,
                n2 INTEGER,
                n3 INTEGER,
                plot_x REAL,
                plot_y REAL,
                session_id TEXT,
                hash_email_session TEXT,
                browser TEXT DEFAULT NULL,
                region TEXT DEFAULT NULL
            );
            """)
            conn.commit()
            print("Database initialized.")
    else:
        print("Database already exists. Initialization skipped.")

# Append a new record
def append_record(
    q1: int, q2: int, q3: int, q4: int, q5: int, q6: int,
    n1: int, n2: int, n3: int, plot_x: float, plot_y: float,
    session_id: str, hash_email_session: Optional[str] = None,
    browser: Optional[str] = None, region: Optional[str] = None
):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO survey_results (
            q1_response, q2_response, q3_response, q4_response, q5_response, q6_response,
            n1, n2, n3, plot_x, plot_y, session_id, hash_email_session, browser, region
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (q1, q2, q3, q4, q5, q6, n1, n2, n3, plot_x, plot_y, session_id, hash_email_session, browser, region))
        conn.commit()

# Read all records
def read_all_records():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM survey_results;")
        return cursor.fetchall()

# Test the setup
if __name__ == "__main__":
    # Initialize the database only if it doesn't already exist
    initialize_database()

    # Append a test record (optional, remove in production)
    append_record(
        q1=1, q2=2, q3=3, q4=4, q5=5, q6=6,
        n1=10, n2=20, n3=30, plot_x=12.34, plot_y=56.78,
        session_id="test_session", hash_email_session="dummy_hash",
        browser="Chrome", region="US"
    )

    # Read and print all records
    records = read_all_records()
    for record in records:
        print(record)
