# src/visualization/report.py

from visualization.ternary_plotter import TernaryPlotter
import matplotlib.pyplot as plt
from typing import List
import logging
from pathlib import Path
from fpdf import FPDF
import io
import sys

# Configure logging
logging.basicConfig(
    filename='debug.log',  # Log file name
    level=logging.INFO,    # Adjust to DEBUG for more verbosity
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

import io
from fpdf import FPDF

def save_to_pdf(user_scores, avg_score, text_summary):
    """
    Generate a PDF report with user scores, average score, and summary text.
    """
    try:
        # Create a PDF object
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt="Survey Report", ln=True, align="C")

        # Average Score
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, txt="Average Score:", ln=True)
        pdf.cell(200, 10, txt=f"PreModern: {avg_score[0]:.2f}, Modern: {avg_score[1]:.2f}, PostModern: {avg_score[2]:.2f}", ln=True)

        # Individual Scores
        pdf.ln(10)
        pdf.cell(200, 10, txt="Individual Scores:", ln=True)
        for i, score in enumerate(user_scores, start=1):
            pdf.cell(200, 10, txt=f"Score {i}: PreModern={score[0]:.2f}, Modern={score[1]:.2f}, PostModern={score[2]:.2f}", ln=True)

        # Summary
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=text_summary)

        # Save PDF to a buffer
        buffer = io.BytesIO()
        pdf.output(dest="S").encode("latin1")  # Generate PDF content
        buffer.write(pdf.output(dest="S").encode("latin1"))
        buffer.seek(0)  # Reset the buffer pointer to the beginning

        # Return the buffer contents
        return buffer.getvalue()
    except Exception as e:
        raise RuntimeError(f"Error generating PDF: {e}")

class SurveyReport:
    def __init__(self):
        self.plotter = TernaryPlotter()
        logging.info("SurveyReport instance created.")

    def create_ternary_chart(self, user_scores: List[List[float]], avg_score: List[float]):
        """Generate ternary plot for the survey results."""
        try:
            logging.info("Creating ternary chart...")
            chart = self.plotter.create_plot(user_scores, avg_score)
            logging.info("Ternary chart created successfully.")
            return chart
        except Exception as e:
            logging.error(f"Error creating ternary chart: {e}")
            raise

    def generate_text_summary(self, avg_score: List[float]) -> str:
        """Create a text summary based on the average score."""
        try:
            logging.info("Generating text summary...")
            summary = (
                f"Your results:\n"
                f"- PreModern: {avg_score[0]:.2f}\n"
                f"- Modern: {avg_score[1]:.2f}\n"
                f"- PostModern: {avg_score[2]:.2f}\n\n"
                "Explanation of PreModern, Modern, and PostModern characteristics..."
            )
            logging.info("Text summary generated successfully.")
            return summary
        except Exception as e:
            logging.error(f"Error generating text summary: {e}")
            raise

    def create_full_report(self, user_scores: List[List[float]], avg_score: List[float]):
        """Combine chart and textual data for the full report."""
        try:
            logging.info("Creating full report...")
            chart = self.create_ternary_chart(user_scores, avg_score)
            text_summary = self.generate_text_summary(avg_score)
            logging.info("Full report created successfully.")
            return chart, text_summary
        except Exception as e:
            logging.error(f"Error creating full report: {e}")
            raise
