from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.sql import text
import logging
from mysql_manager import DatabaseManager
from typing import Optional
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SurveyResponse(BaseModel):
    q1_response: int = Field(..., ge=1, le=6)
    q2_response: int = Field(..., ge=1, le=6)
    q3_response: int = Field(..., ge=1, le=6)
    q4_response: int = Field(..., ge=1, le=6)
    q5_response: int = Field(..., ge=1, le=6)
    q6_response: int = Field(..., ge=1, le=6)
    n1: int = Field(..., ge=0, le=600)
    n2: int = Field(..., ge=0, le=600)
    n3: int = Field(..., ge=0, le=600)
    plot_x: float = Field(..., ge=-100, le=100)
    plot_y: float = Field(..., ge=-100, le=100)
    browser: Optional[str] = None
    region: Optional[str] = None
    source: str = 'test'

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
try:
    db_manager = DatabaseManager()
    logger.info("Database manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database manager: {e}")
    db_manager = None

@app.post("/api/test")
async def test_endpoint():
    return {"message": "test endpoint working"}

@app.get("/api/health")
async def health_check():
    if db_manager is None:
        return {
            "status": "partial",
            "message": "Application running but database connection failed"
        }
    try:
        with db_manager.get_session() as session:
            session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/api/test-survey")
async def test_survey(response: SurveyResponse):
    logger.info("Processing test survey submission")
    try:
        session_id = str(uuid.uuid4())
        
        query = text("""
            INSERT INTO survey_results 
            (session_id, q1_response, q2_response, q3_response, q4_response, 
             q5_response, q6_response, n1, n2, n3, plot_x, plot_y, 
             browser, region, source)
            VALUES 
            (:session_id, :q1_response, :q2_response, :q3_response, :q4_response,
             :q5_response, :q6_response, :n1, :n2, :n3, :plot_x, :plot_y,
             :browser, :region, :source)
        """)
        
        with db_manager.get_session() as session:
            result = session.execute(query, {
                **response.dict(),
                "session_id": session_id
            })
            session.commit()
            
            # Verify the insert
            verify_query = text(
                "SELECT id FROM survey_results WHERE session_id = :session_id"
            )
            verify_result = session.execute(
                verify_query, 
                {"session_id": session_id}
            ).fetchone()
            
            if verify_result:
                return {
                    "status": "success",
                    "message": "Survey response recorded",
                    "session_id": session_id,
                    "record_id": verify_result[0]
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Database insert could not be verified"
                )
                
    except Exception as e:
        logger.error(f"Error processing survey: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)