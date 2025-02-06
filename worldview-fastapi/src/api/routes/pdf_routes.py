# src/api/routes/pdf_routes.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, List
import tempfile
import base64
import os
import logging
from src.visualization.pdf_generator import ModernityPDFReport, generate_pdf_report

router = APIRouter()
logger = logging.getLogger(__name__)

class PDFGenerationRequest(BaseModel):
    perspective: str
    scores: List[float]
    category_responses: Dict[str, str]
    plot_image: str = None  # Base64 encoded plot image

@router.post("/generate-pdf")
async def generate_pdf_endpoint(request: PDFGenerationRequest):
    """Handle PDF generation request"""
    try:
        plot_image_path = None
        
        # If plot image is provided, save it temporarily
        if request.plot_image:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                plot_image_path = tmp.name
                img_data = base64.b64decode(request.plot_image.split(',')[1])
                tmp.write(img_data)

        # Generate PDF using our updated generator function
        pdf_bytes = generate_pdf_report(
            perspective=request.perspective,
            scores=request.scores,
            category_responses=request.category_responses,
            plot_image_path=plot_image_path
        )

        # Clean up temporary file if it was created
        if plot_image_path and os.path.exists(plot_image_path):
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