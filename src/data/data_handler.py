import sqlite3
import json
from datetime import datetime
from typing import Dict, List


class DataHandler:
    def __init__(self, responses_path: str = 'questionnaire_responses.db', max_questions: int = 10, conn=None):
        """Initialize DataHandler with a database connection"""
        self.responses_path = responses_path
        self.max_questions = max_questions
        self.conn = conn or sqlite3.connect(self.responses_path)  # Use provided or create a new connection
        self.initialize_database()

    def initialize_database(self):
        """Initialize database schema if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                responses TEXT,
                scores TEXT,
                aggregate_response TEXT
            )
        ''')
        self.conn.commit()

    def save_response(self, responses: Dict[str, List[int]], scores: List[List[float]]):
        """Save a survey response"""
        avg_score = self.calculate_average_score(scores)
        cursor = self.conn.cursor()
        cursor.execute(
            '''INSERT INTO responses 
            (timestamp, responses, scores, aggregate_response) 
            VALUES (?, ?, ?, ?)''',
            (
                datetime.now().isoformat(),
                json.dumps(responses),
                json.dumps(scores),
                json.dumps(avg_score)
            )
        )
        self.conn.commit()

    def get_responses(self, limit: int = 100):
        """Retrieve responses with flexibility"""
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM responses ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [
            {
                **dict(row),
                'responses': json.loads(row['responses']),
                'scores': json.loads(row['scores']),
                'aggregate_response': json.loads(row['aggregate_response'])
            }
            for row in rows
        ]

    def calculate_average_score(self, scores: List[List[float]]) -> List[float]:
        """Calculate average score from a list of scores"""
        return [round(sum(x) / len(scores), 2) for x in zip(*scores)]