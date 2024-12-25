# src/data/data_handler.py

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List
import json
import logging
from .sqlite_utils import SQLiteManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DataHandler:
    def __init__(self, responses_path: str = 'questionnaire_responses.db', max_questions: int = 10):
        """Initialize DataHandler with database connection"""
        self.responses_path = responses_path
        self.max_questions = max_questions

        # Just verify we can connect to the database
        conn = sqlite3.connect(self.responses_path)
        conn.close()

    def calculate_average_score(self, scores: List[List[float]]) -> List[float]:
        """Calculate average score from a list of scores"""
        return [round(sum(x) / len(scores), 2) for x in zip(*scores)]

    def save_response(self, responses: Dict[str, List[int]], scores: List[List[float]]):
        """Save a survey response"""
        avg_score = self.calculate_average_score(scores)
        
        conn = sqlite3.connect(self.responses_path)
        try:
            cursor = conn.cursor()
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
            conn.commit()
            logger.debug("Response saved successfully")
        except Exception as e:
            logger.error(f"Error saving response: {e}")
            raise
        finally:
            conn.close()

class DataHandler:
    def __init__(self, responses_path: str = 'questionnaire_responses.db', max_questions: int = 10):
        """Initialize DataHandler with database connection"""
        self.responses_path = responses_path
        self.max_questions = max_questions

        # Just verify we can connect to the database
        conn = sqlite3.connect(self.responses_path)
        conn.close()

    def save_response(self, responses: Dict[str, List[int]], scores: List[List[float]]):
        """Save a survey response"""
        avg_score = self.calculate_average_score(scores)
        
        conn = sqlite3.connect(self.responses_path)
        try:
            cursor = conn.cursor()
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
            conn.commit()
            logger.debug("Response saved successfully")
        except Exception as e:
            logger.error(f"Error saving response: {e}")
            raise
        finally:
            conn.close()

    def get_responses(self, limit: int = 100):
        """Retrieve responses with flexibility"""
        conn = sqlite3.connect(self.responses_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM responses ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries and parse JSON
            return [{
                **dict(row),
                'responses': json.loads(row['responses']),
                'scores': json.loads(row['scores']),
                'aggregate_response': json.loads(row['aggregate_response'])
            } for row in rows]
        finally:
            conn.close()

    def calculate_average_score(self, scores: List[List[float]]) -> List[float]:
        """Calculate average score from a list of scores"""
        return [round(sum(x) / len(scores), 2) for x in zip(*scores)]