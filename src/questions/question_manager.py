import json
import random
from dataclasses import dataclass
from typing import List, Dict, Optional
import os
from pathlib import Path

@dataclass
class Question:
    """Class to represent a single question with its responses"""
    text: str
    responses: List[Dict]

class QuestionManager:
    def __init__(self, json_path: str = None):
        """Initialize QuestionManager with path to questions JSON file"""
        if json_path is None:
            # Get the project root directory (where app.py is)
            project_root = Path(__file__).parent.parent.parent
            self.json_path = os.path.join(project_root, 'src', 'data', 'questions_responses.json')
        else:
            self.json_path = json_path
        self.questions = self._load_questions()
    
    def _load_questions(self) -> Dict[str, Question]:
        """Load questions from JSON file"""
        try:
            with open(self.json_path, 'r') as file:
                data = json.load(file)
            
            return {
                key: Question(value["text"], value["responses"])
                for key, value in data["questions"].items()
            }
        except FileNotFoundError:
            raise FileNotFoundError(f"Questions file not found at {self.json_path}")
    
    def get_randomized_options(self, q_key: str, session_state: dict) -> List[Dict]:
        """Get or create randomized options for a question"""
        if "randomised_responses" not in session_state:
            session_state.randomised_responses = {}
        if q_key not in session_state.randomised_responses:
            session_state.randomised_responses[q_key] = random.sample(
                self.questions[q_key].responses,
                len(self.questions[q_key].responses)
            )
        return session_state.randomised_responses[q_key]
    
    def get_question_text(self, q_key: str) -> str:
        """Get the text for a specific question"""
        return self.questions[q_key].text
    
    def get_all_question_keys(self) -> List[str]:
        """Get all question keys"""
        return list(self.questions.keys())
    
    def validate_responses(self, responses: Dict[str, str], scores: List[List[float]]) -> bool:
        """
        Validate that all questions have been answered and scores are valid
        Returns: True if valid, False otherwise
        """
        if len(responses) != len(self.questions):
            return False
            
        if not all(isinstance(score, list) and len(score) == 3 
                  and all(isinstance(val, (int, float)) for val in score)
                  for score in scores):
            return False
            
        return True