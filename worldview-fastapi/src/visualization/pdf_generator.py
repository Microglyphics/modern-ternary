# src/visualization/pdf_generator.py

from fpdf import FPDF
import io
from typing import List, Dict
import tempfile
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernityPDFReport:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_left_margin(15)
        self.pdf.set_right_margin(15)
        
    def add_header(self):
        """Add header and title to the PDF"""
        self.pdf.set_font("Arial", style="B", size=24)
        self.pdf.cell(0, 15, txt="Modernity Worldview Analysis", ln=True, align='C')
        self.pdf.ln(5)
        
        # Add date
        self.pdf.set_font("Arial", size=10)
        current_date = datetime.now().strftime("%B %d, %Y")
        self.pdf.cell(0, 10, txt=f"Report generated on {current_date}", ln=True, align='C')
        self.pdf.ln(10)

    def add_disclaimer(self):
        """Add disclaimer and footer text"""
        self.pdf.set_font("Arial", style="I", size=10)
        self.pdf.multi_cell(0, 5, 
            txt="The Worldview Analysis is not a scientific survey. It is designed as an experiment to provide directional insights.",
            align='L'
        )
        self.pdf.ln(3)
        
        # Add blog URL and copyright
        self.pdf.set_font("Arial", size=10)
        self.pdf.write(5, "For more information, visit ")
        self.pdf.set_text_color(0, 0, 255)
        self.pdf.write(5, "http://philosophics.blog")
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.write(5, f". All Rights Reserved © {datetime.now().year} Bry Willis, Philosophics")

    def add_perspective_summary(self, perspective: str, scores: List[float]):
        """Add perspective summary section"""
        self.pdf.set_font("Arial", size=14)
        self.pdf.write(10, "Your modernity worldview perspective is: ")
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.write(10, perspective)
        self.pdf.ln(15)
        
        # Add scores
        self.pdf.set_font("Arial", size=12)
        self.pdf.cell(0, 10, txt="Your Perspective Scores:", ln=True)
        scores_text = [
            f"PreModern: {scores[0]:.1f}%",
            f"Modern: {scores[1]:.1f}%",
            f"PostModern: {scores[2]:.1f}%"
        ]
        for score in scores_text:
            self.pdf.cell(0, 8, txt=score, ln=True)
        self.pdf.ln(10)

    def add_visualization(self, plot_image_path: str):
        """Add the ternary plot visualization"""
        if os.path.exists(plot_image_path):
            self.pdf.image(plot_image_path, x=25, w=160)
            self.pdf.ln(10)
        else:
            logger.error(f"Plot image not found at {plot_image_path}")

    def add_category_analysis(self, category_responses: Dict[str, str]):
        """Add detailed category analysis"""
        self.pdf.add_page()
        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Worldview Category Analysis", ln=True)
        self.pdf.ln(5)

        for category, response in category_responses.items():
            # Category header
            self.pdf.set_font("Arial", style="B", size=13)
            self.pdf.cell(0, 10, txt=category, ln=True)
            
            # Category content
            self.pdf.set_font("Arial", size=11)
            self.pdf.multi_cell(0, 8, txt=response)
            self.pdf.ln(5)

def generate_pdf_report(perspective: str, scores: List[float], 
                       category_responses: Dict[str, str], plot_image_path: str = None) -> bytes:
    """Generate the complete PDF report"""
    try:
        report = ModernityPDFReport()
        report.add_header()
        report.add_perspective_summary(perspective, scores)
        
        if plot_image_path:
            report.add_visualization(plot_image_path)
            
        report.add_category_analysis(category_responses)
        report.add_disclaimer()

        # Return PDF as bytes
        return report.pdf.output(dest='S').encode('latin-1')
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise