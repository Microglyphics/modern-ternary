from typing import Dict, List
import json
from pathlib import Path

class PerspectiveAnalyzer:
    """Analyzes survey responses to determine perspective types and provide template responses"""
    
    CATEGORIES = ['PreModern', 'Modern', 'PostModern']
    
    @staticmethod
    def get_perspective_summary(scores: List[float]) -> Dict:
        """[Previous method remains the same]"""
        # ... [Previous implementation]

    @staticmethod
    def get_perspective_description(analysis: Dict) -> str:
        """
        Generate a human-readable description of the perspective analysis.
        
        Args:
            analysis: Dictionary from get_perspective_summary()
            
        Returns:
            String description of the perspective
        """
        # Check for 100% score
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

    @staticmethod
    def get_template_responses(analysis: Dict) -> Dict[str, str]:
        """
        Get appropriate template responses for each category based on analysis.
        
        Args:
            analysis: Dictionary from get_perspective_summary()
            
        Returns:
            Dictionary mapping category names to template responses
        """
        try:
            # Load templates
            template_path = Path(__file__).parent.parent / "data" / "response_templates.json"
            with open(template_path) as f:
                templates = json.load(f)["categories"]

            # Determine perspective type for template lookup
            perspective_type = analysis['primary']
            if analysis['strength'] != 'Strong' and analysis['secondary']:
                perspective_type = f"{analysis['primary']}-{analysis['secondary']}"
            elif analysis['strength'] == 'Mixed':
                perspective_type = 'Modern-Balanced'

            # Get responses for each category
            responses = {}
            for category in templates:
                if perspective_type in templates[category]:
                    responses[category] = templates[category][perspective_type]["response"]
                else:
                    # Fall back to primary category if blend isn't found
                    primary = perspective_type.split('-')[0]
                    responses[category] = templates[category][primary]["response"]

            return responses
            
        except Exception as e:
            raise RuntimeError(f"Error loading or processing templates: {e}")

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
        
        result = {
            'primary': primary,
            'strength': None,
            'secondary': None,
            'scores': scores
        }

        # Determine strength and secondary influence
        if max_score == 100:
            result['strength'] = 'Pure'
        elif max_score > 70:
            result['strength'] = 'Strong'
        elif max_score < 50:
            result['strength'] = 'Mixed'
        else:
            result['strength'] = 'Moderate'
            # Check for secondary influence
            other_scores = scores.copy()
            other_scores.pop(primary_idx)
            score_diff = other_scores[0] - other_scores[1]
            if abs(score_diff) > 10:
                secondary_idx = scores.index(max(other_scores))
                result['secondary'] = PerspectiveAnalyzer.CATEGORIES[secondary_idx]
        
        return result