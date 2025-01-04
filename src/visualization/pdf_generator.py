# src/visualization/pdf_generator.py

from fpdf import FPDF
import io
from .perspective_analyzer import PerspectiveAnalyzer
from .ternary_plotter import TernaryPlotter
import tempfile
import os
import logging
from typing import List, Dict
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class SurveyPDFReport:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_left_margin(15)
        self.pdf.set_right_margin(15)
        self.plotter = TernaryPlotter()

    def add_title(self):
        """Add title to the PDF"""
        self.pdf.set_font("Arial", style="B", size=24)
        self.pdf.cell(0, 15, txt="Worldview Analysis", ln=True)
        self.pdf.ln(10)

    def add_perspective_summary(self, scores: list):
        """Add perspective summary section"""
        # Get analysis and description
        analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
        description = PerspectiveAnalyzer.get_perspective_description(analysis)
        
        # Add perspective header
        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Overall Perspective", ln=True)
        self.pdf.ln(5)
        
        # Add description
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(0, 10, txt=description, ln=True)
        self.pdf.ln(5)

    def add_visualization_section(self, scores: list, individual_scores: List[List[float]] = None):
        """Add visualization section with ternary plot"""
        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Perspective Visualization", ln=True)
        self.pdf.ln(5)

        try:
            # Create the plot with individual scores if provided
            chart = self.plotter.create_plot(
                user_scores=individual_scores if individual_scores else [], 
                avg_score=scores
            )
            
            # Save to temporary file with high DPI for quality
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                temp_path = tmp_file.name
                chart.savefig(temp_path, format='png', dpi=300, bbox_inches='tight')
                
                # Add to PDF with consistent dimensions for Letter size
                plot_width = 180
                plot_height = plot_width * 0.85
                x_offset = (215.9 - plot_width) / 2  # Center on Letter page
                self.pdf.image(temp_path, x=x_offset, w=plot_width, h=plot_height)
            
            # Cleanup
            os.unlink(temp_path)
            chart.clear()
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            self.pdf.cell(0, 10, txt="Error generating visualization", ln=True)
        
        self.pdf.ln(10)

    def add_category_analysis(self, scores: list, category_responses: dict):
        """Add the detailed category analysis section"""
        from .perspective_analyzer import PerspectiveAnalyzer
        analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
        perspective_type = analysis['primary']
        if analysis['strength'] != 'Strong' and analysis['secondary']:
            perspective_type = f"{analysis['primary']}-{analysis['secondary']}"
        elif analysis['strength'] == 'Mixed':
            perspective_type = 'Modern-Balanced'

        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Category Analysis", ln=True)
        self.pdf.ln(5)

        # Load response templates
        template_path = Path(__file__).parent.parent / "data" / "response_templates.json"
        try:
            with open(template_path) as f:
                templates = json.load(f)["categories"]
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            templates = {}

        # Process each category
        for category in ["Source of Truth", "Understanding the World", 
                        "Knowledge Acquisition", "World View", 
                        "Societal Values", "Identity"]:
            # Add category header
            self.pdf.set_font("Arial", style="B", size=14)
            self.pdf.cell(0, 10, txt=category, ln=True)
            
            # Get the detailed template response
            if category in templates:
                category_templates = templates[category]
                if perspective_type in category_templates:
                    template_response = category_templates[perspective_type]["response"]
                else:
                    # Fall back to primary category if blend isn't found
                    primary = perspective_type.split('-')[0]
                    template_response = category_templates.get(primary, {}).get("response", 
                        "Template not found for this perspective.")
            else:
                template_response = "Category templates not found."
            
            # Add template response
            self.pdf.set_font("Arial", size=12)
            self.pdf.multi_cell(0, 8, txt=template_response)
            self.pdf.ln(5)

    def save_to_buffer(self):
        """Save PDF to buffer"""
        try:
            buffer = io.BytesIO()
            self.pdf.output(dest="S").encode("latin1")
            buffer.write(self.pdf.output(dest="S").encode("latin1"))
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error in save_to_buffer: {e}")
            raise RuntimeError(f"Error saving PDF to buffer: {e}")

def generate_survey_report(scores: list, category_responses: dict, individual_scores: List[List[float]] = None):
    """Generate the complete survey report"""
    try:
        report = SurveyPDFReport()
        report.add_title()
        report.add_perspective_summary(scores)
        report.add_visualization_section(scores, individual_scores)
        report.add_category_analysis(scores, category_responses)
        return report.save_to_buffer()
    except Exception as e:
        logger.error(f"Error in report generation: {e}")
        raise RuntimeError(f"Error generating survey report: {e}")