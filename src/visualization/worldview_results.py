# src/visualization/worldview_results.py

import streamlit as st
from .ternary_plotter import TernaryPlotter
from .perspective_analyzer import PerspectiveAnalyzer
from typing import Dict, List
import json
from pathlib import Path

class ResponseTemplateManager:
    """Manages response templates for different worldview categories"""
    
    def __init__(self, template_path: str = "src/data/response_templates.json"):
        """Initialize with path to templates JSON file"""
        self.template_path = Path(template_path)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load templates from JSON file"""
        try:
            with open(self.template_path) as f:
                return json.load(f)["categories"]
        except Exception as e:
            st.error(f"Error loading templates: {e}")
            return {}

    def get_perspective_type(self, scores: List[float]) -> str:
        """
        Determine the perspective type based on score distribution.
        Uses PerspectiveAnalyzer for sophisticated analysis.
        
        Args:
            scores: List of [PreModern, Modern, PostModern] percentages
        
        Returns:
            String indicating the perspective type
        """
        analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
        
        # For template selection, we'll use a simplified mapping
        if analysis['strength'] == 'Mixed':
            return "Modern-Balanced"  # Default template for mixed perspectives
        
        # For strong or moderate with no secondary, use primary
        if analysis['strength'] == 'Strong' or not analysis['secondary']:
            return analysis['primary']
            
        # For moderate with secondary influence
        return f"{analysis['primary']}-{analysis['secondary']}"

    def get_response_for_category(self, category: str, scores: List[float]) -> str:
        """Get the appropriate response template for a category based on scores"""
        perspective = self.get_perspective_type(scores)
        
        category_templates = self.templates.get(category, {})
        if perspective not in category_templates:
            # Fall back to the primary category if the exact blend isn't found
            primary = perspective.split('-')[0]
            perspective = primary
            
        perspective_data = category_templates.get(perspective, {})
        return perspective_data.get("response", "No template available for this perspective.")

def display_results_page(scores: List[float], category_responses: Dict[str, str], plotter=None):
    """
    Display the complete results page with template responses
    
    Args:
        scores: List of [PreModern, Modern, PostModern] percentages
        category_responses: Dictionary of category-response pairs
        plotter: Optional TernaryPlotter instance
    """
    template_manager = ResponseTemplateManager()
    analyzer = PerspectiveAnalyzer()
    
    # High-level Summary Section
    st.title("Worldview Analysis")
    
    analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
    description = PerspectiveAnalyzer.get_perspective_description(analysis)
    
    st.header("Overall Perspective")
    st.subheader(description)
    
    st.write(f"""
    PreModern: {scores[0]:.1f}%  
    Modern: {scores[1]:.1f}%  
    PostModern: {scores[2]:.1f}%
    """)
    
    # Ternary Plot Section
    st.header("Perspective Visualization")
    
    if plotter is None:
        plotter = TernaryPlotter()
    
    chart = plotter.create_plot(user_scores=[], avg_score=scores)
    plotter.display_plot(chart)
    
    # Detailed Category Analysis
    st.header("Category Analysis")
    
    # Process each category
    for category, user_response in category_responses.items():
        st.subheader(category)
        
        # Get template response if available
        template_response = template_manager.get_response_for_category(category, scores)
        if template_response != "No template available for this perspective.":
            st.write(template_response)
        else:
            st.write(user_response)
        
        st.markdown("---")