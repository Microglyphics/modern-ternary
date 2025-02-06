# api/routes/pdf_routes.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, List
import tempfile
import base64
import logging
import os
from src.visualization.pdf_generator import ModernityPDFReport

router = APIRouter()
logger = logging.getLogger(__name__)

class PDFGenerationRequest(BaseModel):
    perspective: str
    scores: List[float]
    category_responses: Dict[str, str]
    plot_image: str = None  # Base64 encoded plot image

@router.post("/generate-pdf")
async def generate_pdf(request: PDFGenerationRequest):
    try:
        plot_image_path = None
        if request.plot_image:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                plot_image_path = tmp.name
                img_data = base64.b64decode(request.plot_image.split(',')[1])
                tmp.write(img_data)

        # Generate PDF
        report = ModernityPDFReport()
        report.add_header()
        report.add_perspective_summary(request.perspective, request.scores)
        
        if plot_image_path:
            report.add_visualization(plot_image_path)
            
        report.add_category_analysis(request.category_responses)
        report.add_disclaimer()

        pdf_bytes = report.pdf.output(dest='S').encode('latin-1')

        # Clean up temporary file
        if plot_image_path:
            try:
                os.unlink(plot_image_path)
            except Exception as e:
                logger.error(f"Error cleaning up temporary file: {e}")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=worldview_analysis.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))