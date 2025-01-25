# main.py
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.security import HTTPBasic
from models import SurveyResponse, Question
from db_manager import DatabaseManager
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Modernity Worldview Analysis API",
    description="API for the Modernity Worldview Analysis survey",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://modernity-worldview.uc.r.appspot.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# Initialize database manager
db = DatabaseManager()

@app.post("/api/test-survey")
async def test_survey(survey: SurveyResponse):
    try:
        logger.info(f"Received survey data: {survey.dict()}")
        
        # Add session_id if not provided
        if not hasattr(survey, 'session_id'):
            survey.session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {survey.session_id}")
        
        try:
            record_id = db.save_response(survey.dict())
            logger.info(f"Saved survey response with record_id: {record_id}")
            
            return {
                "status": "success",
                "message": "Survey response recorded",
                "session_id": survey.session_id,
                "record_id": record_id
            }
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(db_error)}"
            )
            
    except Exception as e:
        logger.error(f"Error processing survey: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing survey: {str(e)}"
        )