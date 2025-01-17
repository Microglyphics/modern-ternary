import pytest
import tempfile
import os
from src.data.sqlite_utils import SQLiteManager

@pytest.fixture
def sqlite_manager():
    """Fixture to create an SQLiteManager with a temporary database."""
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    manager = SQLiteManager(db_path=temp_db.name)
    try:
        yield manager
    finally:
        # Explicitly close the database connections
        try:
            with manager.get_connection() as conn:
                conn.close()
        except Exception:
            pass  # Ignore errors if the connection is already closed

        # Clean up the temporary database file
        temp_db.close()
        try:
            os.unlink(temp_db.name)
        except PermissionError:
            pass  # Ignore errors if the file is still locked


def test_ensure_table_exists(sqlite_manager):
    """Test that the responses table is created."""
    with sqlite_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='responses';")
        table = cursor.fetchone()
        assert table is not None, "Table 'responses' should exist"

def test_save_response(sqlite_manager):
    """Test saving a response to the database."""
    test_responses = {"question1": "Answer A", "question2": "Answer B"}
    test_scores = [[3.5, 4.0, 2.5], [4.0, 3.0, 3.5]]

    sqlite_manager.save_response(test_responses, test_scores)

    # Verify the response was saved correctly
    with sqlite_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM responses ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        assert row is not None, "Row should be inserted"
        assert row["responses"] == '{"question1": "Answer A", "question2": "Answer B"}'
        assert row["scores"] == '[[3.5, 4.0, 2.5], [4.0, 3.0, 3.5]]'

def test_get_responses(sqlite_manager):
    """Test retrieving responses from the database."""
    test_responses = {"question1": "Answer A", "question2": "Answer B"}
    test_scores = [[3.5, 4.0, 2.5], [4.0, 3.0, 3.5]]

    sqlite_manager.save_response(test_responses, test_scores)
    responses = sqlite_manager.get_responses(limit=1)

    assert len(responses) == 1, "Should retrieve one response"
    assert responses[0]["responses"] == {"question1": "Answer A", "question2": "Answer B"}
    assert responses[0]["scores"] == [[3.5, 4.0, 2.5], [4.0, 3.0, 3.5]]
