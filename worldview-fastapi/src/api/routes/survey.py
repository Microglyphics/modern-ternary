# src/lib/types/survey.py
from pydantic import BaseModel

class SurveyResponse(BaseModel):
   session_id: str
   q1_response: int 
   q2_response: int
   q3_response: int
   q4_response: int
   q5_response: int
   q6_response: int

# src/routes/api/survey.py
from fastapi import APIRouter, HTTPException
from ...lib.types.survey import SurveyResponse
from ...lib.db.mysql import get_db_config
import mysql.connector

router = APIRouter()

@router.post("/submit")
async def submit_survey(response: SurveyResponse):
   try:
       conn = mysql.connector.connect(**get_db_config())
       cursor = conn.cursor()
       cursor.execute("""
           INSERT INTO survey_results 
           (session_id, q1_response, q2_response, q3_response, 
            q4_response, q5_response, q6_response)
           VALUES (%s, %s, %s, %s, %s, %s, %s)
       """, (response.session_id, response.q1_response, response.q2_response,
             response.q3_response, response.q4_response, response.q5_response, 
             response.q6_response))
       conn.commit()
       return {"success": True}
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))