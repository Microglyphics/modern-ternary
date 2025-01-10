# src/data/db_manager.py
import mysql.connector
from mysql.connector import pooling
import pandas as pd
import json
from datetime import datetime
import logging
from typing import Dict, List, Optional
from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MySQLManager:
    def __init__(self, db_config: Dict[str, str]):
        """Initialize MySQL manager with connection pool
        Args:
            db_config: Dictionary containing connection settings
        """
        self.pool_config = {
            "pool_name": "survey_pool",
            "pool_size": 5,
            **db_config
        }
        self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.pool_config)
        logger.debug(f"Initializing MySQLManager with host: {db_config['host']}")
        with self.get_connection() as conn:
            logger.debug("Database connection successful")

    @contextmanager
    def get_connection(self):
        """Get database connection from pool with context management"""
        conn = self.pool.get_connection()
        try:
            yield conn
        finally:
            conn.close()

    def save_response(self, responses, scores, metadata):
        """Save a survey response to the database."""
        try:
            # Debugging output
            # logger.debug(f"Saving responses: {responses}")
            # logger.debug(f"Scores to insert: n1={scores[0]}, n2={scores[1]}, n3={scores[2]}")
            # logger.debug(f"Metadata: {metadata}")

            # Insert into the database
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    INSERT INTO survey_results (
                        q1_response, q2_response, q3_response, q4_response, q5_response, q6_response,
                        n1, n2, n3, plot_x, plot_y, session_id, hash_email_session, browser, region, source
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''',
                    (
                        responses.get("Q1"),
                        responses.get("Q2"),
                        responses.get("Q3"),
                        responses.get("Q4"),
                        responses.get("Q5"),
                        responses.get("Q6"),
                        scores[0],  # n1
                        scores[1],  # n2
                        scores[2],  # n3
                        metadata.get("plot_x"),
                        metadata.get("plot_y"),
                        metadata.get("session_id"),
                        metadata.get("hash_email_session"),
                        metadata.get("browser"),
                        metadata.get("region"),
                        metadata.get("source"),
                    )
                )
                conn.commit()
                logger.debug("Insert into survey_results successful.")
        except mysql.connector.Error as db_err:
            logger.error(f"MySQL Error: {db_err.msg}")
            raise
        except Exception as e:
            logger.error(f"General error: {e}", exc_info=True)
            raise

    def get_responses(self, limit: Optional[int] = 100) -> List[Dict]:
        """Retrieve responses from database"""
        try:
            logger.debug(f"Attempting to retrieve {limit} responses")
            
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT * FROM responses ORDER BY timestamp DESC"
                if limit:
                    query += f" LIMIT {limit}"
                logger.debug(f"Executing query: {query}")
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if not rows:
                    logger.debug("No responses found in database")
                    return []
                
                # Parse JSON strings
                result = []
                for row in rows:
                    row['responses'] = json.loads(row['responses'])
                    row['scores'] = json.loads(row['scores'])
                    row['aggregate_response'] = json.loads(row['aggregate_response'])
                    result.append(row)
                
                logger.debug(f"Returning {len(result)} responses")
                return result
                
        except Exception as e:
            logger.error(f"Error retrieving responses: {e}", exc_info=True)
            return []

    def get_aggregate_scores(self, limit: Optional[int] = 100) -> pd.DataFrame:
        """Get aggregate scores for analysis"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT aggregate_response FROM responses ORDER BY timestamp DESC"
                if limit:
                    query += f" LIMIT {limit}"
                    
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if not rows:
                    return pd.DataFrame(columns=['PreModern', 'Modern', 'PostModern'])
                
                # Parse JSON strings to lists
                scores_list = [json.loads(row['aggregate_response']) for row in rows]
                return pd.DataFrame(
                    scores_list, 
                    columns=['PreModern', 'Modern', 'PostModern']
                )
        except Exception as e:
            logger.error(f"Error retrieving aggregate scores: {e}")
            return pd.DataFrame(columns=['PreModern', 'Modern', 'PostModern'])