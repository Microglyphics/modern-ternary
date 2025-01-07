# src/data/db_manager.py

import os
import sqlite3
from typing import List, Optional
from src.core.question_manager import QuestionManager

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
                region TEXT DEFAULT NULL,
                source TEXT DEFAULT 'local'
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
    browser: Optional[str] = None, region: Optional[str] = None,
    source: str = 'local', version: Optional[str] = None
):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO survey_results (
            q1_response, q2_response, q3_response, q4_response, q5_response, q6_response,
            n1, n2, n3, plot_x, plot_y, session_id, hash_email_session, browser, region, 
            source, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (q1, q2, q3, q4, q5, q6, n1, n2, n3, plot_x, plot_y, session_id, 
              hash_email_session, browser, region, source, version))
        conn.commit()

# Read all records
def read_all_records():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM survey_results;")
        return cursor.fetchall()

# In streamlit_app.py

def get_response_number(response_text: str, q_key: str, question_manager: QuestionManager) -> int:
    """
    Get the response number (R-value) for a given response text.
    
    Args:
        response_text: The selected response text
        q_key: The question key (e.g., 'Q1')
        question_manager: Instance of QuestionManager
    
    Returns:
        Integer value from the response ID (e.g., 5 from 'Q1R5')
    """
    responses = question_manager.get_responses(q_key)
    for response in responses:
        if response['text'] == response_text:
            # Extract the number after 'R' from the ID
            return response['r_value']
    return None

def save_survey_results(session_state, question_manager):
    """
    Save survey results to the database using the response ID numbers.
    """
    # Get response numbers for each question
    q1_value = get_response_number(
        session_state.get('radio_Q1'), 
        'Q1', 
        question_manager
    )
    q2_value = get_response_number(
        session_state.get('radio_Q2'), 
        'Q2', 
        question_manager
    )
    q3_value = get_response_number(
        session_state.get('radio_Q3'), 
        'Q3', 
        question_manager
    )
    q4_value = get_response_number(
        session_state.get('radio_Q4'), 
        'Q4', 
        question_manager
    )
    q5_value = get_response_number(
        session_state.get('radio_Q5'), 
        'Q5', 
        question_manager
    )
    q6_value = get_response_number(
        session_state.get('radio_Q6'), 
        'Q6', 
        question_manager
    )

    # Calculate N values and plot coordinates (assuming these are needed)
    # This is a placeholder - adjust according to your actual calculation needs
    n1, n2, n3 = calculate_n_values(session_state)
    plot_x, plot_y = calculate_plot_coordinates(n1, n2, n3)

    # Save to database
    append_record(
        q1=q1_value,
        q2=q2_value,
        q3=q3_value,
        q4=q4_value,
        q5=q5_value,
        q6=q6_value,
        n1=n1,
        n2=n2,
        n3=n3,
        plot_x=plot_x,
        plot_y=plot_y,
        session_id=st.session_state.get('session_id', 'default'),
        hash_email_session=None  # Add if you implement email hashing
    )


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
