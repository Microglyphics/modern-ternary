from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from src.data.mysql_manager import db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SurveyResponse(BaseModel):
    session_id: str
    answers: Dict[str, Dict[str, float]]  # Will store scores for each question
    source: str = 'web'
    browser: Optional[str] = None
    version: str = '2.0.0'

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In development, can be more specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/submit")
async def submit_survey(response: SurveyResponse):
    try:
        print("Received survey response:", response.dict())  # Debug log
        
        # Initialize db_record with required fields
        db_record = {
            "session_id": response.session_id,
            "source": response.source,
            "browser": response.browser,
            "q1_response": None,
            "q2_response": None,
            "q3_response": None,
            "q4_response": None,
            "q5_response": None,
            "q6_response": None,
            "n1": 0,
            "n2": 0,
            "n3": 0,
            "plot_x": 0.0,
            "plot_y": 0.0
        }

        # Process responses ensuring values are within constraints
        total_scores = [0, 0, 0]
        for question_id, answer_data in response.answers.items():
            q_num = int(question_id.replace('Q', ''))
            response_num = answer_data.get('response_num', 1)
            # Ensure response is within 1-6 range
            response_num = max(1, min(6, response_num))
            db_record[f'q{q_num}_response'] = response_num

            # Accumulate scores
            scores = answer_data.get('scores', [0, 0, 0])
            total_scores = [total_scores[i] + scores[i] for i in range(3)]

        # Calculate averages
        num_questions = len(response.answers)
        if num_questions > 0:
            db_record['n1'] = min(600, max(0, round((total_scores[0] / num_questions) * 6)))
            db_record['n2'] = min(600, max(0, round((total_scores[1] / num_questions) * 6)))
            db_record['n3'] = min(600, max(0, round((total_scores[2] / num_questions) * 6)))
            
            # Calculate plot coordinates
            db_record['plot_x'] = float(((db_record['n2'] - db_record['n1']) / 6))
            db_record['plot_y'] = float(((db_record['n3'] - ((db_record['n1'] + db_record['n2']) / 2)) / 6))

        print("Final DB record:", db_record)  # Debug log

        # Insert with explicit transaction
        with db_manager.get_session() as session:
            try:
                query = """
                    INSERT INTO survey_results 
                    (session_id, q1_response, q2_response, q3_response, 
                    q4_response, q5_response, q6_response, n1, n2, n3, 
                    plot_x, plot_y, source, browser)
                    VALUES 
                    (:session_id, :q1_response, :q2_response, :q3_response,
                    :q4_response, :q5_response, :q6_response, :n1, :n2, :n3,
                    :plot_x, :plot_y, :source, :browser)
                """
                result = session.execute(query, db_record)
                session.commit()  # Explicitly commit the transaction
                print("Insert successful, rows affected:", result.rowcount)
                
                # Verify the insert
                verify_query = "SELECT id FROM survey_results WHERE session_id = :session_id"
                verify_result = session.execute(verify_query, {"session_id": response.session_id}).fetchone()
                print("Verified insert, new record id:", verify_result[0] if verify_result else None)
                
                return {"status": "success", "session_id": response.session_id}
            except Exception as db_error:
                session.rollback()
                print("Database error:", str(db_error))
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    
    except Exception as e:
        print("General error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))