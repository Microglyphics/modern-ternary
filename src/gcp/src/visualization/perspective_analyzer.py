# src/visualization/perspective_analyzer.py
from typing import Dict, List

class PerspectiveAnalyzer:
    """Analyzes ternary plot coordinates to determine perspective types and influences"""
    
    CATEGORIES = ['PreModern', 'Modern', 'PostModern']
    
    @staticmethod
    def get_perspective_summary(scores: List[float]) -> Dict:
        """
        Analyze scores to determine primary and secondary perspectives.
        
        Args:
            scores: List of [PreModern, Modern, PostModern] percentages
            
        Returns:
            Dictionary containing:
            - primary: Primary perspective
            - strength: 'Strong', 'Moderate', or 'Mixed'
            - secondary: Secondary perspective (if applicable)
            - scores: Original scores for reference
        """
        # Ensure scores sum to 100 (within floating point tolerance)
        if not (99.9 <= sum(scores) <= 100.1):
            raise ValueError("Scores must sum to approximately 100")
            
        # Get category with highest score
        max_score = max(scores)
        primary_idx = scores.index(max_score)
        primary = PerspectiveAnalyzer.CATEGORIES[primary_idx]
        
        # Initial result dictionary
        result = {
            'primary': primary,
            'strength': None,
            'secondary': None,
            'scores': scores
        }
        
        # Pure perspective (100%)
        if max_score == 100:
            result['strength'] = 'Pure'
            return result
            
        # Strong perspective (>70%)
        if max_score > 70:
            result['strength'] = 'Strong'
            return result
            
        # Mixed perspective (<50%)
        if max_score < 50:
            result['strength'] = 'Mixed'
            return result
            
        # Moderate perspective (50-70%)
        result['strength'] = 'Moderate'
        
        # Analyze potential secondary influence
        other_scores = scores.copy()
        other_scores.pop(primary_idx)
        score_diff = other_scores[0] - other_scores[1]
        
        # If difference between secondary scores is significant (>10%)
        if abs(score_diff) > 10:
            secondary_idx = scores.index(max(other_scores))
            result['secondary'] = PerspectiveAnalyzer.CATEGORIES[secondary_idx]
            
        return result
    
    @staticmethod
    def get_perspective_description(analysis: Dict) -> str:
        """
        Generate a human-readable description of the perspective analysis.
        
        Args:
            analysis: Dictionary from get_perspective_summary()
            
        Returns:
            String description of the perspective
        """
        # Check for 100% score first
        if max(analysis['scores']) == 100:
            return f"Pure {analysis['primary']}"
            
        if analysis['strength'] == 'Mixed':
            return "Mixed Perspective"
            
        description = ""
        if analysis['strength'] == 'Strong':
            description = f"Strongly {analysis['primary']}"
        else:  # Moderate
            if analysis['secondary']:
                description = f"Moderately {analysis['primary']} with {analysis['secondary']} influences"
            else:
                description = f"Moderately {analysis['primary']}"
                
        return description