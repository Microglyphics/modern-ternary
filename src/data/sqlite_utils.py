# src/data/sqlite_utils.py
import sqlite3
import pandas as pd
import json
from datetime import datetime
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SQLiteManager:
    def __init__(self, db_path: str = 'questionnaire_responses.db'):
        """Initialize SQLite manager for storing survey responses"""
        self.db_path = db_path
        logger.debug(f"Initializing SQLiteManager with database path: {db_path}")
        self.ensure_table_exists()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def ensure_table_exists(self):
        """Create responses table if it doesn't exist"""
        logger.debug("Checking/creating responses table")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Get list of tables first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.debug(f"Existing tables in database: {tables}")
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                responses TEXT NOT NULL,  -- JSON string of question responses
                scores TEXT NOT NULL,     -- JSON string of individual scores
                aggregate_response TEXT NOT NULL  -- JSON string of averaged scores
            )''')
            conn.commit()
            
            # Verify table was created
            cursor.execute("SELECT * FROM responses LIMIT 1")
            columns = [description[0] for description in cursor.description]
            logger.debug(f"Table columns: {columns}")

    # Rest of your methods remain the same
    
    def save_response(self, responses: Dict[str, str], scores: List[List[float]]):
        """Save a survey response"""
        try:
            logger.debug(f"Attempting to save response: {responses}")
            logger.debug(f"With scores: {scores}")
            
            # Calculate average scores
            avg_score = [round(sum(x) / len(scores), 2) for x in zip(*scores)]
            logger.debug(f"Calculated average scores: {avg_score}")
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Log the data being inserted
                responses_json = json.dumps(responses)
                scores_json = json.dumps(scores)
                avg_score_json = json.dumps(avg_score)
                
                logger.debug(f"JSON data to insert:")
                logger.debug(f"responses: {responses_json}")
                logger.debug(f"scores: {scores_json}")
                logger.debug(f"aggregate_response: {avg_score_json}")
                
                cursor.execute(
                    '''INSERT INTO responses 
                    (timestamp, responses, scores, aggregate_response)
                    VALUES (?, ?, ?, ?)''',
                    (
                        datetime.now().isoformat(),
                        responses_json,
                        scores_json,
                        avg_score_json
                    )
                )
                conn.commit()
                
                # Verify the insert
                cursor.execute("SELECT * FROM responses ORDER BY id DESC LIMIT 1")
                last_row = cursor.fetchone()
                logger.debug(f"Last inserted row: {last_row}")
                
        except Exception as e:
            logger.error(f"Error saving response: {e}", exc_info=True)
            raise
    
    def get_responses(self, limit: Optional[int] = 100) -> List[Dict]:
        """Retrieve responses from database"""
        try:
            logger.debug(f"Attempting to retrieve {limit} responses from {self.db_path}")
            
            with self.get_connection() as conn:
                # First check if table exists and has data
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM responses")
                count = cursor.fetchone()[0]
                logger.debug(f"Found {count} total responses in database")
                
                query = "SELECT * FROM responses ORDER BY timestamp DESC"
                if limit:
                    query += f" LIMIT {limit}"
                logger.debug(f"Executing query: {query}")
                
                df = pd.read_sql_query(query, conn)
                logger.debug(f"Retrieved DataFrame with shape: {df.shape}")
                
                if df.empty:
                    logger.debug("No responses found in database")
                    return []
                
                # Parse JSON strings
                df['responses'] = df['responses'].apply(json.loads)
                df['scores'] = df['scores'].apply(json.loads)
                df['aggregate_response'] = df['aggregate_response'].apply(json.loads)
                
                result = df.to_dict(orient='records')
                logger.debug(f"Returning {len(result)} responses")
                return result
                
        except Exception as e:
            logger.error(f"Error retrieving responses: {e}", exc_info=True)
            return []
    
    # In src/data/sqlite_utils.py, add to SQLiteManager class
    def get_aggregate_scores(self, limit: Optional[int] = 100) -> pd.DataFrame:
        """Get aggregate scores for analysis"""
        try:
            with self.get_connection() as conn:
                query = "SELECT aggregate_response FROM responses ORDER BY timestamp DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                df = pd.read_sql_query(query, conn)
                
                if df.empty:
                    return pd.DataFrame(columns=['PreModern', 'Modern', 'PostModern'])
                
                # Parse JSON strings to lists
                scores_list = df['aggregate_response'].apply(json.loads).tolist()
                return pd.DataFrame(
                    scores_list, 
                    columns=['PreModern', 'Modern', 'PostModern']
                )
        except Exception as e:
            logger.error(f"Error retrieving aggregate scores: {e}")
            return pd.DataFrame(columns=['PreModern', 'Modern', 'PostModern'])