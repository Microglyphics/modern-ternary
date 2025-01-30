# main.py
import os
from pathlib import Path
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.models.models import SurveyResponse
from src.api.db_manager import DatabaseManager
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get base directory for data files
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Modernity Worldview Analysis API",
    description="API for the Modernity Worldview Analysis survey",
    version="1.0.0"
)

# Configure templates and static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

def load_questions():
    try:
        with open(BASE_DIR / "src" / "data" / "questions_responses.json") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        raise HTTPException(status_code=500, detail="Error loading questions")

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

@app.get("/")
async def serve_survey(request: Request):
    """Serve the main survey page"""
    return templates.TemplateResponse("survey.html", {"request": request})
    
@app.get("/api/health")
async def health_check():
    """Check API and database health"""
    try:
        db.connect()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": str(e)
        }

@app.get("/api/questions")
async def get_questions():
    """Get survey questions"""
    try:
        questions = load_questions()
        return questions
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submit")
async def submit_survey(response: SurveyResponse):
    """Submit survey responses"""
    try:
        if not hasattr(response, 'session_id'):
            response.session_id = str(uuid.uuid4())
        
        record_id = db.save_response(response.dict())
        return {
            "status": "success",
            "message": "Survey response recorded",
            "session_id": response.session_id,
            "record_id": record_id
        }
    except Exception as e:
        logger.error(f"Error saving survey: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/debug")
async def debug():
    """Debug endpoint to verify file paths and directory structure"""
    try:
        BASE_DIR = Path(__file__).resolve().parent
        return {
            "current_dir": str(BASE_DIR),
            "files": [str(f) for f in BASE_DIR.glob("**/*") if not str(f).startswith(str(BASE_DIR / 'node_modules'))],
            "src_exists": (BASE_DIR / "src").exists(),
            "data_exists": (BASE_DIR / "src" / "data").exists(),
            "questions_exists": (BASE_DIR / "src" / "data" / "questions_responses.json").exists(),
            "templates_exists": (BASE_DIR / "src" / "templates").exists(),
            "survey_exists": (BASE_DIR / "src" / "templates" / "survey.html").exists()
        }
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "test endpoint working"}

@app.post("/api/test-survey")
async def test_survey(survey: SurveyResponse):
    """Test survey submission"""
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
