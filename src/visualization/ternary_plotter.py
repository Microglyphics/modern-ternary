import ternary
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np

class TernaryPlotter:
    def __init__(self, scale=100):
        self.scale = scale
        # Define colors
        self.colors = {
            'dots': '#0052CC',  # Vibrant blue
            'star': '#DE0000',  # Bright red
            'grid': '#E0E0E0',  # Light gray
            'border': '#000000' # Black
        }
     
    
    def create_plot(self, user_scores, avg_score=None):
        """
        Create a ternary plot with user scores and optional average score.
        
        Parameters:
        - user_scores: List of [PreModern, Modern, PostModern] scores for each response
        - avg_score: Optional average score to highlight
        """
        # Create figure and tax
        fig, tax = ternary.figure(scale=self.scale)
        fig.set_size_inches(10, 8)  # Adjust figure size
        
        # Configure the base plot
        tax.boundary(linewidth=1.5)
        tax.gridlines(
            multiple=10,
            color='gray',        
            linewidth=0.8,       
            alpha=0.4            
        )
        
        # Remove default matplotlib axes
        tax.clear_matplotlib_ticks()
        
        # Configure vertex labels with simple offset
        label_kwargs = {
            'fontsize': 16,
            'fontfamily': 'Arial',
            'offset': 0.3
        }
        
        # Use corner label methods with basic parameters
        tax.left_corner_label("PostModern", **label_kwargs)
        tax.right_corner_label("PreModern", **label_kwargs)
        tax.top_corner_label("Modern", **label_kwargs)
        
        # Plot individual scores with larger markers
        if user_scores:
            tax.scatter(
                user_scores,
                marker='o',
                color=self.colors['dots'],
                s=100,
                label="Individual Scores",
                zorder=3
            )
        
        # Plot and annotate average score
        if avg_score:
            # Plot star marker
            tax.scatter(
                [avg_score],
                marker='*',
                color=self.colors['star'],
                s=300,
                label="Aggregated Score",
                zorder=4
            )
            
            import os
            from matplotlib.offsetbox import OffsetImage, AnnotationBbox
            import matplotlib.pyplot as plt
            
            try:
                # Get absolute path to the star image
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                star_path = os.path.join(project_root, 'src', 'visualization', 'red_star.png')
                
                # Load the PNG image
                star_img = plt.imread(star_path)
                star_image = OffsetImage(star_img, zoom=0.08)
                star_box = AnnotationBbox(
                    star_image,
                    (0.42, 0.075),  # Moved star lower
                    frameon=False,
                    box_alignment=(1, 0.5),
                    xycoords='figure fraction'
                )
                plt.gca().add_artist(star_box)
            except Exception as e:
                print(f"Could not load star image: {e}")

            # Create score text without box
            score_text = f"   {avg_score[0]:.1f}, {avg_score[1]:.1f}, {avg_score[2]:.1f}"
            plt.figtext(
                0.425, 0.111,  # Moved text up
                score_text,
                ha='center',
                va='center',
                fontsize=14,
                fontfamily='Arial',
                color=self.colors['star']
            )
        
        # Configure legend
        tax.legend(
            loc='upper right',
            bbox_to_anchor=(0.95, 0.95),
            frameon=True,
            fontsize=10
        )
        
        # Adjust layout to prevent clipping
        plt.tight_layout(pad=1.5)
        
        return fig

    def display_plot(self, figure):
        """Display the plot in Streamlit"""
        st.pyplot(figure)