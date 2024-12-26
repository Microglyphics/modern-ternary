import streamlit as st
import ternary
import matplotlib.pyplot as plt

class TernaryPlotter:
    def __init__(self, scale=100):
        self.scale = scale
        
    def create_plot(self, user_scores, avg_score=None):
        """
        Create a ternary plot with user scores and optional average score.

        Parameters:
        user_scores: List of [PreModern, Modern, PostModern] scores
        avg_score: Optional average score to highlight
        """
        import ternary

        # Create the figure and tax
        scale = 100  # Adjust as needed
        figure, tax = ternary.figure(scale=scale)
        tax.boundary(linewidth=1.5)
        tax.gridlines(multiple=10, color="gray", linewidth=0.5)

        # Add axis labels
        tax.left_axis_label("PreModern", fontsize=12, offset=0.16)
        tax.right_axis_label("Modern", fontsize=12, offset=0.16)
        tax.bottom_axis_label("PostModern", fontsize=12, offset=0.04)

        # Plot individual scores
        if user_scores:
            tax.scatter(
                user_scores,
                marker='o',
                color='blue',  # Single color
                s=50,
                label="Individual Scores"
            )

        # Plot average score if provided
        if avg_score:
            tax.scatter(
                [avg_score],
                marker='*',
                color='red',
                s=200,
                label="Average Score"
            )
            tax.annotate(
                f"Avg: {avg_score[0]:.1f}, {avg_score[1]:.1f}, {avg_score[2]:.1f}",
                position=avg_score,
                fontsize=10,
                ha="center",
                va="bottom",
                color="red"
            )

        # Add legend
        tax.legend()

        return figure

    
    def display_plot(self, figure):
        """Display the plot in Streamlit"""
        st.pyplot(figure)
