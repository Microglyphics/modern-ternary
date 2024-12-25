import streamlit as st
import ternary
import matplotlib.pyplot as plt

class TernaryPlotter:
    def __init__(self, scale=100):
        self.scale = scale
        
    def create_plot(self, user_scores, avg_score=None):
        """
        Create a ternary plot with user scores and optional average score
        
        Parameters:
        user_scores: List of [premodern, modern, postmodern] scores
        avg_score: Optional average score to highlight
        """
        # Create the figure and tax
        figure, tax = ternary.figure(scale=self.scale)
        tax.boundary(linewidth=1.5)
        tax.gridlines(multiple=10, color="gray", linewidth=0.5)

        # Add axis labels
        tax.left_axis_label("PreModern", fontsize=12, offset=0.16)
        tax.right_axis_label("Modern", fontsize=12, offset=0.16)
        tax.bottom_axis_label("PostModern", fontsize=12, offset=0.04)

        # Plot individual scores
        if user_scores:
            tax.scatter(user_scores, marker='o', color='blue', label="Individual Scores")

        # Plot average score if provided
        if avg_score:
            tax.scatter([avg_score], marker='o', color='red', label="Aggregated Score")
            
            # Add annotation for average score
            tax.annotate(
                f"PreModern: {avg_score[0]:.2f}, Modern: {avg_score[1]:.2f}, PostModern: {avg_score[2]:.2f}",
                position=(50, -10),
                ha="center",
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.5", edgecolor="red", facecolor="white")
            )

        # Add legend
        tax.legend()
        
        return figure
    
    def display_plot(self, figure):
        """Display the plot in Streamlit"""
        st.pyplot(figure)
