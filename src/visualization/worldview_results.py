# src/visualization/worldview_results.py

import streamlit as st
from .ternary_plotter import TernaryPlotter
from .perspective_analyzer import PerspectiveAnalyzer
from .pdf_generator import generate_survey_report  # Moved import to top
from typing import Dict, List
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        """
        analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
        
        if analysis['strength'] == 'Mixed':
            return "Modern-Balanced"
            
        if analysis['strength'] == 'Strong' or not analysis['secondary']:
            return analysis['primary']
            
        return f"{analysis['primary']}-{analysis['secondary']}"

    def get_response_for_category(self, category: str, scores: List[float]) -> str:
        """Get the appropriate response template for a category based on scores"""
        perspective = self.get_perspective_type(scores)
        
        category_templates = self.templates.get(category, {})
        if perspective not in category_templates:
            primary = perspective.split('-')[0]
            perspective = primary
            
        perspective_data = category_templates.get(perspective, {})
        return perspective_data.get("response", "No template available for this perspective.")

def display_results_page(scores: List[float], category_responses: Dict[str, str], individual_scores: List[List[float]] = None):
    """Display the complete results page with template responses"""
    template_manager = ResponseTemplateManager()
    
    st.title("Worldview Analysis")
    
    # Get and display perspective analysis
    analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
    description = PerspectiveAnalyzer.get_perspective_description(analysis)
    
    st.header("Overall Perspective")
    st.markdown(f"**{description}**")
    
    st.write(f"""
    PreModern: {scores[0]:.1f}%  
    Modern: {scores[1]:.1f}%  
    PostModern: {scores[2]:.1f}%
    """)
    
    # Visualization Section
    st.header("Perspective Visualization")
    plotter = TernaryPlotter()
    chart = plotter.create_plot(
        user_scores=individual_scores if individual_scores else [], 
        avg_score=scores
    )
    plotter.display_plot(chart)
    
    # Add visual spacing before Category Analysis
    st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
    
    # Category Analysis on new "page"
    st.header("Category Analysis")
    
    for category, user_response in category_responses.items():
        st.subheader(category)
        template_response = template_manager.get_response_for_category(category, scores)
        
        if template_response != "No template available for this perspective.":
            st.write(template_response)
        else:
            st.write(user_response)
        
        st.markdown("---")

    # PDF Generation and Download - single button that handles everything
    st.download_button(
        label="Download Report",
        data=generate_survey_report(scores, category_responses, individual_scores),
        file_name="worldview_analysis.pdf",
        mime="application/pdf",
        use_container_width=True
    )