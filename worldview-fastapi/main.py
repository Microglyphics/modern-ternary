# Debugging MySQL connexion
from contextlib import contextmanager

# main.py
# Standard library imports
import os
from pathlib import Path
import logging
import uuid
import json
from decimal import Decimal

# Third-party imports
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from src.api.routes import pdf_routes

# Local application imports
from models import SurveyResponse, Question
from db_manager import DatabaseManager
from src.visualization.perspective_analyzer import PerspectiveAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create single database manager instance
logger.info("Creating database manager instance")
db_manager = DatabaseManager()
logger.info("Database manager created")

# Get base directory for data files
BASE_DIR = Path(__file__).resolve().parent

# Create FastAPI app
app = FastAPI(
    title="Modernity Worldview Analysis API",
    description="API for the Modernity Worldview Analysis survey",
    version="1.0.0"
)

# Add a context manager for database operations
@contextmanager
def get_db():
    logger.info("Entering database context")
    try:
        logger.info("Attempting to connect database")
        db_manager.connect()
        logger.info("Database connected successfully")
        yield db_manager
    except Exception as e:
        logger.error(f"Database context error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Exiting database context")
        try:
            if hasattr(db_manager, 'connection') and db_manager.connection:
                db_manager.connection.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

@app.post("/api/submit")
async def submit_survey(response: SurveyResponse):
    logger.info("🚀 Starting submit_survey endpoint")

    try:
        data = response.dict()

        # Convert Decimal fields to float
        for key in data:
            if isinstance(data[key], Decimal):
                data[key] = float(data[key])

        logger.info(f"📥 Received survey data: {json.dumps(data, indent=2, default=decimal_to_float)}")

        # Save the response
        record_id = db_manager.save_response(data)
        logger.info(f"✅ Saved survey response with ID: {record_id}")

        return {
            "status": "success",
            "message": "Survey response recorded",
            "session_id": response.session_id,
            "record_id": record_id
        }

    except Exception as e:
        logger.error(f"❌ Error saving survey: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
# Setup templates - add this right after app creation
templates = Jinja2Templates(directory="templates")

# Create a custom StaticFiles instance for JSX files
class JSXStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if path.endswith('.jsx'):
            response.headers['content-type'] = 'text/javascript'
        return response

# Mount static files
app.mount("/static", JSXStaticFiles(directory="static"), name="static")

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

app.include_router(pdf_routes.router, prefix="/api")

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
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "connect-src 'self' https://unpkg.com"
    )
    return response

@app.get("/")
async def root(request: Request):
    logger.info("Handling root request")
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def load_questions():
    try:
        path = BASE_DIR / "src" / "data" / "questions_responses.json"
        logger.info(f"Attempting to load questions from: {path}")
        
        with open(path) as f:
            data = json.load(f)
            logger.info(f"Questions data loaded: {data.keys()}")  # Log the keys
            if "questions" not in data:
                logger.error("No 'questions' key in loaded data")
                return None
            logger.info(f"Questions loaded successfully: {len(data['questions'])} questions")
            return data
            
    except Exception as e:
        logger.error(f"Error loading questions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading questions: {str(e)}")

def load_templates():
    try:
        path = BASE_DIR / "src" / "data" / "response_templates.json"
        logger.info(f"Attempting to load templates from: {path}")
        
        with open(path) as f:
            data = json.load(f)
            logger.info(f"Templates data loaded: {data.keys()}")  # Log the keys
            if "categories" not in data:
                logger.error("No 'categories' key in loaded data")
                return None
            logger.info(f"Templates loaded successfully: {len(data['categories'])} categories")
            return data["categories"]
            
    except Exception as e:
        logger.error(f"Error loading templates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading templates: {str(e)}")

@app.post("/api/analyze")
async def analyze_survey(responses: dict):
    try:
        logger.info(f"Received responses: {responses}")
        
        # Load and check questions data
        questions_data = load_questions()
        logger.info(f"Questions data type: {type(questions_data)}")
        if not questions_data or "questions" not in questions_data:
            raise HTTPException(status_code=500, detail="Invalid questions data format")
            
        questions = questions_data["questions"]
        logger.info(f"Questions loaded: {len(questions)} questions")
        
        # Load and check templates
        templates = load_templates()
        logger.info(f"Templates type: {type(templates)}")
        if not templates:
            raise HTTPException(status_code=500, detail="Invalid templates data format")
        
        # Calculate perspective scores
        logger.info("Calculating perspective scores...")
        total_scores = calculate_perspective_scores(responses, questions)
        logger.info(f"Calculated scores: {total_scores}")
        
        # Get analysis and description
        analysis = PerspectiveAnalyzer.get_perspective_summary(total_scores)
        description = PerspectiveAnalyzer.get_perspective_description(analysis)
        
        # Get category responses
        category_responses = get_category_responses(analysis, templates)
        
        return {
            "status": "success",
            "perspective": description,
            "scores": total_scores,
            "analysis": analysis,
            "category_responses": category_responses
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_survey: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/api/health")
async def health_check():
    try:
        db_manager.connect()  # This will reconnect if needed
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": str(e)
        }
    
@app.get("/api/db-health")
async def db_health():
    """Test database connection from FastAPI."""
    try:
        connection = db_manager.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        connection.close()
        return {"status": "healthy", "db_result": result[0]}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
    
@app.get("/debug-paths")
async def debug_paths():
    base = Path(__file__).resolve().parent
    template_dir = base / "templates"
    index_path = template_dir / "index.html"
    
    return {
        "base_dir": str(base),
        "templates_dir": str(template_dir),
        "templates_exists": template_dir.exists(),
        "index_exists": index_path.exists(),
        "index_path": str(index_path),
        "template_files": [str(p) for p in template_dir.glob("*")] if template_dir.exists() else []
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
        questions = load_questions()
        logger.info(f"Returning questions data: {questions}")
        return questions
    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        return {"error": str(e)}
    
@app.post("/api/analyze")
async def analyze_survey(responses: dict):
    try:
        logger.info(f"Received responses: {responses}")
        
        questions_data = load_questions()["questions"]
        logger.info(f"Loaded questions data")
        
        templates = load_templates()
        logger.info(f"Loaded templates")
        
        # Calculate perspective scores
        logger.info("Calculating perspective scores...")
        total_scores = calculate_perspective_scores(responses, questions_data)
        logger.info(f"Calculated scores: {total_scores}")
        
        # Get analysis and description
        logger.info("Getting perspective analysis...")
        analysis = PerspectiveAnalyzer.get_perspective_summary(total_scores)
        logger.info(f"Analysis: {analysis}")
        
        description = PerspectiveAnalyzer.get_perspective_description(analysis)
        logger.info(f"Description: {description}")
        
        # Get category responses based on analysis
        logger.info("Getting category responses...")
        category_responses = get_category_responses(analysis, templates)
        
        response_data = {
            "status": "success",
            "perspective": description,
            "scores": total_scores,
            "analysis": analysis,
            "category_responses": category_responses
        }
        logger.info(f"Returning response: {response_data}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error analyzing survey: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def calculate_perspective_scores(responses: dict, questions_data: dict) -> list:
    """Calculate aggregate perspective scores from survey responses."""
    total_scores = [0, 0, 0]  # [PreModern, Modern, PostModern]
    
    for q_id, response_num in responses.items():
        if response_num is not None:  # Skip any None responses
            question = questions_data[q_id]
            # Response numbers are 1-based, list indices are 0-based
            response_idx = response_num - 1
            if 0 <= response_idx < len(question["responses"]):
                scores = question["responses"][response_idx]["scores"]
                total_scores = [a + b for a, b in zip(total_scores, scores)]
    
    # Convert to percentages
    total = sum(total_scores)
    if total > 0:
        normalized_scores = [round((score / total) * 100, 1) for score in total_scores]
        # Ensure scores sum to exactly 100
        adjustment = 100 - sum(normalized_scores)
        normalized_scores[-1] += adjustment  # Add any rounding difference to last score
        return normalized_scores
    return [0, 0, 0]

def get_category_responses(analysis: dict, templates: dict) -> dict:
    """Get appropriate template responses for each category based on analysis."""
    perspective_type = analysis['primary']
    if analysis['strength'] != 'Strong' and analysis['secondary']:
        perspective_type = f"{analysis['primary']}-{analysis['secondary']}"
    elif analysis['strength'] == 'Mixed':
        perspective_type = 'Modern-Balanced'
        
    category_responses = {}
    for category in templates:
        if perspective_type in templates[category]:
            category_responses[category] = templates[category][perspective_type]["response"]
        else:
            # Fall back to primary category if blend isn't found
            primary = perspective_type.split('-')[0]
            category_responses[category] = templates[category][primary]["response"]
            
    return category_responses    

@app.get("/api/check-files")
async def check_files():
    base = Path(__file__).resolve().parent
    q_path = base / "src" / "data" / "questions_responses.json"
    t_path = base / "src" / "data" / "response_templates.json"
    
    return {
        "base_dir": str(base),
        "questions_file_exists": q_path.exists(),
        "questions_path": str(q_path),
        "templates_file_exists": t_path.exists(),
        "templates_path": str(t_path)
    }
 
@app.post("/api/test")
async def test_endpoint():
    return {"message": "test endpoint working"}

@app.get("/api/test-route")
async def test_route():
    return {"status": "route exists"}

@app.get("/api/test-db")
@app.get("/api/test-db")
async def test_db():
    """Test database connection."""
    logger.info("Starting database connection test")
    try:
        result = db_manager.test_connection()
        logger.info(f"Test completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/connexion-test")
async def test_connection():
    """Test database connection and return detailed diagnostics"""
    try:
        # Get environment info
        env_info = {
            "GAE_ENV": os.getenv('GAE_ENV'),
            "INSTANCE_CONNECTION_NAME": os.getenv('INSTANCE_CONNECTION_NAME'),
            "DB_HOST": os.getenv('DB_HOST'),
            "DB_PORT": os.getenv('DB_PORT')
        }
        
        # Test database connexion
        result = db_manager.test_connection()
        
        return {
            "status": "success",
            "environment": env_info,
            "connection_test": result
        }
    except Exception as e:
        logger.error(f"Connexion test failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "environment": env_info
        }