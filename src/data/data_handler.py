from datetime import datetime
import pandas as pd
from typing import Dict, List, Union

class DataHandler:
    def __init__(self, responses_path: str = 'survey_responses.csv'):
        """Initialize DataHandler with path to responses file"""
        self.responses_path = responses_path
        
    def save_response(self, responses: Dict[str, str], scores: List[List[float]]) -> None:
        """
        Save a survey response
        Args:
            responses: Dictionary of question keys to response texts
            scores: List of [premodern, modern, postmodern] scores
        """
        # Calculate average score
        avg_score = [sum(x) / len(scores) for x in zip(*scores)]
        
        # Create new response row
        new_response = pd.DataFrame([{
            'timestamp': datetime.now().isoformat(),
            'responses': str(responses),
            'scores': str(scores),
            'avg_score': str(avg_score)
        }])
        
        # Append to CSV
        try:
            # Try to append to existing file
            new_response.to_csv(self.responses_path, mode='a', header=False, index=False)
        except FileNotFoundError:
            # Create new file if it doesn't exist
            new_response.to_csv(self.responses_path, index=False)
            
    def calculate_average_score(self, scores: List[List[float]]) -> List[float]:
        """Calculate average score from a list of scores"""
        return [sum(x) / len(scores) for x in zip(*scores)]
