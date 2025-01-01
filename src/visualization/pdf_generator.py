# src/visualization/pdf_generator.py
from fpdf import FPDF
import io
from .perspective_analyzer import PerspectiveAnalyzer
from .ternary_plotter import TernaryPlotter
from .worldview_results import ResponseTemplateManager  # Add this import
import time
import logging

logger = logging.getLogger(__name__)

class SurveyPDFReport:
    def __init__(self):
        start = time.time()
        logger.debug("Initializing PDF report...")
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_left_margin(15)
        self.pdf.set_right_margin(15)
        self.plotter = TernaryPlotter()
        logger.debug(f"PDF initialization took {time.time() - start:.2f} seconds")

    def add_title(self):
        start = time.time()
        logger.debug("Adding title...")
        self.pdf.set_font("Arial", style="B", size=24)
        self.pdf.cell(0, 15, txt="Worldview Analysis", ln=True)
        self.pdf.ln(10)
        logger.debug(f"Title addition took {time.time() - start:.2f} seconds")

    def add_perspective_summary(self, scores: list):
        start = time.time()
        logger.debug("Adding perspective summary...")
        analysis = PerspectiveAnalyzer.get_perspective_summary(scores)
        description = PerspectiveAnalyzer.get_perspective_description(analysis)

        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Overall Perspective", ln=True)
        self.pdf.ln(5)
        
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(0, 10, txt=description, ln=True)
        self.pdf.ln(5)
        
        self.pdf.set_font("Arial", style="I", size=12)
        self.pdf.cell(0, 8, txt=f"PreModern: {scores[0]:.1f}%", ln=True)
        self.pdf.cell(0, 8, txt=f"Modern: {scores[1]:.1f}%", ln=True)
        self.pdf.cell(0, 8, txt=f"PostModern: {scores[2]:.1f}%", ln=True)
        self.pdf.ln(15)
        logger.debug(f"Perspective summary took {time.time() - start:.2f} seconds")

    def add_visualization_section(self, scores: list):
        start = time.time()
        logger.debug("Adding visualization section...")
        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Perspective Visualization", ln=True)
        self.pdf.ln(5)

        # Create the plot
        logger.debug("Creating ternary plot...")
        plot_start = time.time()
        chart = self.plotter.create_plot(user_scores=[], avg_score=scores)
        logger.debug(f"Plot creation took {time.time() - plot_start:.2f} seconds")
        
        # Save to temporary file
        import tempfile
        import os
        
        logger.debug("Saving plot to temp file...")
        save_start = time.time()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            temp_path = tmp_file.name
            chart.savefig(temp_path, format='png', dpi=150)  # Reduced DPI
        logger.debug(f"Plot save took {time.time() - save_start:.2f} seconds")
            
        # Add to PDF
        logger.debug("Adding plot to PDF...")
        add_start = time.time()
        plot_width = 180
        plot_height = plot_width * 0.8
        self.pdf.image(temp_path, x=15, w=plot_width, h=plot_height)
        logger.debug(f"PDF addition took {time.time() - add_start:.2f} seconds")
        
        # Cleanup
        logger.debug("Cleaning up temporary files...")
        cleanup_start = time.time()
        os.unlink(temp_path)
        chart.clear()
        logger.debug(f"Cleanup took {time.time() - cleanup_start:.2f} seconds")
        
        self.pdf.ln(10)
        logger.debug(f"Total visualization section took {time.time() - start:.2f} seconds")

    def add_category_analysis(self, scores: list):
        start = time.time()
        logger.debug("Adding category analysis...")
        self.pdf.set_font("Arial", style="B", size=18)
        self.pdf.cell(0, 12, txt="Category Analysis", ln=True)
        self.pdf.ln(5)

        template_manager = ResponseTemplateManager()
        categories = {
            "Source of Truth": None,
            "Understanding the World": None,
            "Knowledge Acquisition": None,
            "World View": None,
            "Societal Values": None,
            "Identity": None
        }

        for category in categories.keys():
            template_response = template_manager.get_response_for_category(category, scores)
            
            self.pdf.set_font("Arial", style="B", size=14)
            self.pdf.cell(0, 10, txt=category, ln=True)
            
            self.pdf.set_font("Arial", size=12)
            self.pdf.multi_cell(0, 8, txt=template_response)
            self.pdf.ln(10)
        logger.debug(f"Category analysis took {time.time() - start:.2f} seconds")

    def save_to_buffer(self):
        start = time.time()
        logger.debug("Saving to buffer...")
        try:
            buffer = io.BytesIO()
            self.pdf.output(dest="S").encode("latin1")
            buffer.write(self.pdf.output(dest="S").encode("latin1"))
            buffer.seek(0)
            logger.debug(f"Buffer save took {time.time() - start:.2f} seconds")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error in save_to_buffer: {e}")
            raise RuntimeError(f"Error saving PDF to buffer: {e}")

def generate_survey_report(scores: list, category_responses: dict):
    total_start = time.time()
    logger.debug("Starting full report generation...")
    try:
        report = SurveyPDFReport()
        report.add_title()
        report.add_perspective_summary(scores)
        report.add_visualization_section(scores)
        report.add_category_analysis(scores)
        result = report.save_to_buffer()
        logger.debug(f"Total report generation took {time.time() - total_start:.2f} seconds")
        return result
    except Exception as e:
        logger.error(f"Error in report generation: {e}")
        raise RuntimeError(f"Error generating survey report: {e}")