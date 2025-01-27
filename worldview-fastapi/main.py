# main.py
import os
from pathlib import Path
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

# Get base directory for data files
BASE_DIR = Path(__file__).resolve().parent

def load_questions():
    try:
        with open(BASE_DIR / "src" / "data" / "questions_responses.json") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        raise HTTPException(status_code=500, detail="Error loading questions")

def load_templates():
    try:
        with open(BASE_DIR / "src" / "data" / "response_templates.json") as f:
            return json.load(f)["categories"]
    except Exception as e:
        logger.error(f"Error loading templates: {e}")
        raise HTTPException(status_code=500, detail="Error loading templates")

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

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' https:; "
        "img-src 'self' https: data:; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "connect-src 'self'"
    )
    return response
@app.get("/")
async def root():
    return {
        "message": "Modernity Worldview Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    try:
        # Test database connection
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

@app.get("/api/debug")
async def debug():
    try:
        BASE_DIR = Path(__file__).resolve().parent
        return {
            "current_dir": str(BASE_DIR),
            "files": [str(f) for f in BASE_DIR.glob("**/*")],
            "src_exists": (BASE_DIR / "src").exists(),
            "data_exists": (BASE_DIR / "src" / "data").exists(),
            "questions_exists": (BASE_DIR / "src" / "data" / "questions_responses.json").exists()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/questions")
async def get_questions():
    try:
        return {"test": "endpoint exists"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/submit")
async def submit_survey(response: SurveyResponse):
    try:
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
    
@app.post("/api/test")
async def test_endpoint():
    return {"message": "test endpoint working"}

@app.get("/api/test-route")
async def test_route():
    return {"status": "route exists"}