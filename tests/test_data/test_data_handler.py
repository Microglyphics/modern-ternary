import pytest
import sqlite3
import json
from src.data.data_handler import DataHandler

@pytest.fixture
def data_handler():
    """Fixture to create a DataHandler using a shared in-memory database."""
    conn = sqlite3.connect(":memory:")  # Shared connection for in-memory database
    handler = DataHandler(responses_path=":memory:", conn=conn)

    # Create the table explicitly in the shared connection
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            responses TEXT,
            scores TEXT,
            aggregate_response TEXT
        )
    ''')
    conn.commit()

    yield handler

    # Close the connection after the test
    conn.close()

def test_initialisation(data_handler: DataHandler):
    """Test that DataHandler initialises correctly."""
    assert isinstance(data_handler, DataHandler), "DataHandler should initialise without errors"

def test_save_response(data_handler: DataHandler):
    """Test saving a response to the database."""
    test_responses = {"question1": [1, 0, 0], "question2": [0, 1, 0]}
    test_scores = [[3.5, 4.0, 2.5], [4.0, 3.0, 3.5]]

    # Save a response
    data_handler.save_response(test_responses, test_scores)

    # Verify the response was saved
    cursor = data_handler.conn.cursor()
    cursor.execute("SELECT * FROM responses ORDER BY id DESC LIMIT 1;")
    row = cursor.fetchone()
    assert row is not None, "Row should be inserted"
    assert json.loads(row[2]) == test_responses, "Responses should match"
    assert json.loads(row[3]) == test_scores, "Scores should match"

def test_get_responses(data_handler: DataHandler):
    """Test retrieving responses from the database."""
    test_responses = {"question1": [1, 0, 0], "question2": [0, 1, 0]}
    test_scores = [[3.5, 4.0, 2.5], [4.0, 3.0, 3.5]]

    data_handler.save_response(test_responses, test_scores)
    responses = data_handler.get_responses(limit=1)

    assert len(responses) == 1, "Should retrieve one response"
    assert responses[0]["responses"] == {"question1": [1, 0, 0], "question2": [0, 1, 0]}
    assert responses[0]["scores"] == [[3.5, 4.0, 2.5], [4.0, 3.0, 3.5]]