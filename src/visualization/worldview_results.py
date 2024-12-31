# src/visualization/worldview_results.py

import streamlit as st
from .ternary_plotter import TernaryPlotter

def get_dominant_perspective(scores):
    """Determine the dominant perspective if any score is >= 67%"""
    pre, mod, post = scores
    if pre >= 67:
        return "PreModern"
    if mod >= 67:
        return "Modern"
    if post >= 67:
        return "PostModern"
    return "Indeterminate"

def display_results_page(scores, category_responses, plotter=None):
    """Display the complete results page"""
    # High-level Summary Section
    st.title("Worldview Analysis")
    
    dominant = get_dominant_perspective(scores)
    st.header("Overall Perspective")
    st.subheader(dominant)
    
    st.write(f"""
    PreModern: {scores[0]:.1f}%  
    Modern: {scores[1]:.1f}%  
    PostModern: {scores[2]:.1f}%
    """)
    
    # Ternary Plot Section
    st.header("Perspective Visualization")
    
    # Use provided plotter or create new one if needed
    if plotter is None:
        plotter = TernaryPlotter()
    
    # Pass empty list for user_scores
    chart = plotter.create_plot(user_scores=[], avg_score=scores)
    plotter.display_plot(chart)
    
    # Detailed Category Analysis
    st.header("Category Analysis")
    
    for category, response in category_responses.items():
        st.subheader(category)
        st.write(response)
        st.markdown("---")