import ternary
import matplotlib.pyplot as plt
import streamlit as st

# Initialize TernaryPlotter
# plotter = TernaryPlotter(scale=100)  # Adjust scale if necessary

class TernaryPlotter:
    def __init__(self, scale=100):
        self.scale = scale

    def create_plot(self, user_scores, avg_score=None):
        """
        Create a ternary plot with user scores and optional average score.

        Parameters:
        - user_scores: List of [PreModern, Modern, PostModern] scores for each response.
        - avg_score: Optional average score to highlight.
        """
        import ternary

        # Create the figure and tax
        figure, tax = ternary.figure(scale=self.scale)
        tax.boundary(linewidth=1.5)
        tax.gridlines(multiple=10, color="gray", linewidth=0.5)

        # Remove X-Y axis labels and ticks
        tax.clear_matplotlib_ticks()

        # Add ternary axis labels at the corners, rendered outside
        tax.left_corner_label("PreModern", fontsize=12, offset=0.2)
        tax.right_corner_label("Modern", fontsize=12, offset=0.2)
        tax.top_corner_label("PostModern", fontsize=12, offset=0.2)

        # Plot individual scores
        if user_scores:
            tax.scatter(
                user_scores,
                marker='o',
                color='blue',
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
