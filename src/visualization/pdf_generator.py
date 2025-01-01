# src/visualization/pdf_generator.py

from fpdf import FPDF
import io
from .perspective_analyzer import PerspectiveAnalyzer

class SurveyPDFReport:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)

    def add_title(self):
        """Add report title"""
        self.pdf.set_font("Arial", style="B", size=16)
        self.pdf.cell(200, 10, txt="Worldview Analysis Report", ln=True, align="C")
        self.pdf.ln(10)

    def add_perspective_summary(self, scores: list):
        """Add the overall perspective summary"""
        analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
        description = PerspectiveAnalyzer.get_perspective_description(analysis)

        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(200, 10, txt="Overall Perspective", ln=True)
        
        self.pdf.set_font("Arial", style="B", size=12)
        self.pdf.cell(200, 10, txt=description, ln=True)
        
        self.pdf.set_font("Arial", size=12)
        self.pdf.cell(200, 10, txt=f"PreModern: {scores[0]:.1f}%", ln=True)
        self.pdf.cell(200, 10, txt=f"Modern: {scores[1]:.1f}%", ln=True)
        self.pdf.cell(200, 10, txt=f"PostModern: {scores[2]:.1f}%", ln=True)
        self.pdf.ln(10)

    def add_category_analysis(self, category_responses: dict):
        """Add detailed category analysis"""
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(200, 10, txt="Category Analysis", ln=True)
        self.pdf.ln(5)

        for category, response in category_responses.items():
            self.pdf.set_font("Arial", style="B", size=12)
            self.pdf.cell(200, 10, txt=category, ln=True)
            
            self.pdf.set_font("Arial", size=12)
            self.pdf.multi_cell(0, 10, txt=response)
            self.pdf.ln(5)

    def save_to_buffer(self):
        """Save the PDF to a buffer and return its contents"""
        try:
            buffer = io.BytesIO()
            self.pdf.output(dest="S").encode("latin1")
            buffer.write(self.pdf.output(dest="S").encode("latin1"))
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            raise RuntimeError(f"Error generating PDF: {e}")

def generate_survey_report(scores: list, category_responses: dict):
    """
    Generate a complete survey report PDF.
    
    Args:
        scores: List of [PreModern, Modern, PostModern] percentages
        category_responses: Dictionary of category-response pairs
    
    Returns:
        PDF contents as bytes
    """
    try:
        report = SurveyPDFReport()
        report.add_title()
        report.add_perspective_summary(scores)
        report.add_category_analysis(category_responses)
        return report.save_to_buffer()
    except Exception as e:
        raise RuntimeError(f"Error generating survey report: {e}")