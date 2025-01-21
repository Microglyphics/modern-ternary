# server/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from sqlalchemy.sql import text
from typing import Dict, List, Optional
from db.mysql_manager import DatabaseManager
import logging
import time
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_manager = DatabaseManager()

class SurveyResponse(BaseModel):
    session_id: str
    source: str
    browser: str
    q1_response: int
    q2_response: int
    q3_response: int
    q4_response: int
    q5_response: int
    q6_response: int
    n1: float
    n2: float
    n3: float
    plot_x: float
    plot_y: float

# Add Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        
        logger.info(f"=== Request Start [{request_id}] ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"URL: {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Get request body for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.body()
                logger.info(f"Request Body: {body.decode()}")
                # Reset body position for next reader
                await request.body()
            except Exception as e:
                logger.error(f"Error reading request body: {e}")
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Process time: {process_time:.3f}s")
            
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info(f"=== Request End [{request_id}] ===")

app = FastAPI()

# Add CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/submit")
async def submit_survey(response: SurveyResponse):
    logger.info("=== Starting Survey Submission ===")
    try:
        logger.info(f"Processing survey response: {json.dumps(response.dict(), indent=2)}")
        
        db_record = response.dict()
        logger.info(f"Prepared database record: {json.dumps(db_record, indent=2)}")

        with db_manager.get_session() as session:
            try:
                query = text("""
                    INSERT INTO survey_results 
                    (session_id, q1_response, q2_response, q3_response, 
                    q4_response, q5_response, q6_response, n1, n2, n3, 
                    plot_x, plot_y, source, browser)
                    VALUES 
                    (:session_id, :q1_response, :q2_response, :q3_response,
                    :q4_response, :q5_response, :q6_response, :n1, :n2, :n3,
                    :plot_x, :plot_y, :source, :browser)
                """)
                
                logger.info("Executing INSERT query")
                result = session.execute(query, db_record)
                session.commit()
                logger.info("Database commit successful")

                # Verify the insert
                verify_query = text(
                    "SELECT id FROM survey_results WHERE session_id = :session_id"
                )
                verify_result = session.execute(
                    verify_query, 
                    {"session_id": response.session_id}
                ).fetchone()
                
                if verify_result:
                    logger.info(f"Record verified with ID: {verify_result[0]}")
                    return {
                        "status": "success",
                        "message": "Survey response recorded successfully",
                        "record_id": verify_result[0]
                    }
                else:
                    logger.error("Insert verification failed - no record found")
                    raise HTTPException(
                        status_code=500,
                        detail="Database insert could not be verified"
                    )

            except Exception as db_error:
                logger.error(f"Database error: {str(db_error)}", exc_info=True)
                session.rollback()
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error: {str(db_error)}"
                )
    
    except Exception as e:
        logger.error(f"Submission error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        logger.info("=== Survey Submission Complete ===")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)