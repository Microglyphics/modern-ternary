# src/visualization/pdf_generator.py

from fpdf import FPDF
import io
from .perspective_analyzer import PerspectiveAnalyzer
from .ternary_plotter import TernaryPlotter
from .worldview_results import ResponseTemplateManager  # Import the template manager

class SurveyPDFReport:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_left_margin(15)
        self.pdf.set_right_margin(15)
        self.plotter = TernaryPlotter()
        self.template_manager = ResponseTemplateManager()

    def add_title(self):
        """Add main title"""
        self.pdf.set_font("Arial", style="B", size=24)
        self.pdf.cell(0, 15, txt="Worldview Analysis", ln=True)
        self.pdf.ln(10)

    def add_perspective_summary(self, scores: list):
        """Add the overall perspective and scores"""
        analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
        description = PerspectiveAnalyzer.get_perspective_description(analysis)

        # Overall Perspective section
        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Overall Perspective", ln=True)
        self.pdf.ln(5)
        
        # Perspective description
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(0, 10, txt=description, ln=True)
        self.pdf.ln(5)
        
        # Score percentages
        self.pdf.set_font("Arial", style="I", size=12)
        self.pdf.cell(0, 8, txt=f"PreModern: {scores[0]:.1f}%", ln=True)
        self.pdf.cell(0, 8, txt=f"Modern: {scores[1]:.1f}%", ln=True)
        self.pdf.cell(0, 8, txt=f"PostModern: {scores[2]:.1f}%", ln=True)
        self.pdf.ln(15)

    def add_visualization_section(self, scores: list):
        """Add visualization section with ternary plot"""
        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Perspective Visualization", ln=True)
        self.pdf.ln(5)

        # Create and get the ternary plot
        figure = self.plotter.create_plot(user_scores=[], avg_score=scores)
        
        # Save the plot to a temporary file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            temp_path = tmp_file.name
            figure.savefig(temp_path, format='png', dpi=300)
        
        # Add the plot to the PDF
        plot_width = 180  # mm
        plot_height = plot_width * 0.8  # Maintain aspect ratio
        self.pdf.image(temp_path, x=15, w=plot_width, h=plot_height)
        
        # Clean up
        figure.clear()
        os.unlink(temp_path)  # Remove temporary file
        self.pdf.ln(10)

    def add_category_analysis(self, scores: list):
        """Add detailed category analysis with full templated responses"""
        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Category Analysis", ln=True)
        self.pdf.ln(5)

        categories = {
            "Source of Truth": None,
            "Understanding the World": None,
            "Knowledge Acquisition": None,
            "World View": None,
            "Societal Values": None,
            "Identity": None
        }

        for category in categories.keys():
            # Get the full template response for this category
            template_response = self.template_manager.get_response_for_category(category, scores)
            
            # Category title
            self.pdf.set_font("Arial", style="B", size=14)
            self.pdf.cell(0, 10, txt=category, ln=True)
            
            # Full templated response text
            self.pdf.set_font("Arial", size=12)
            self.pdf.multi_cell(0, 8, txt=template_response)
            self.pdf.ln(10)

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
    Generate a complete survey report PDF with visualization.
    """
    try:
        report = SurveyPDFReport()
        report.add_title()
        report.add_perspective_summary(scores)
        report.add_visualization_section(scores)
        report.add_category_analysis(scores)  # Just pass scores, we'll get templates directly
        return report.save_to_buffer()
    except Exception as e:
        raise RuntimeError(f"Error generating survey report: {e}")