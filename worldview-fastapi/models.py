# models.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class Response(BaseModel):
    id: str
    text: str
    scores: List[float]

class Question(BaseModel):
    text: str
    responses: List[Response]

class Questions(BaseModel):
    questions: Dict[str, Question]

class SurveyResponse(BaseModel):
    session_id: Optional[str] = None
    source: str = "web"
    browser: Optional[str] = None
    q1_response: Optional[int] = None
    q2_response: Optional[int] = None
    q3_response: Optional[int] = None
    q4_response: Optional[int] = None
    q5_response: Optional[int] = None
    q6_response: Optional[int] = None
    n1: Optional[float] = None
    n2: Optional[float] = None
    n3: Optional[float] = None
    plot_x: Optional[float] = None
    plot_y: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "q1_response": 1,
                "q2_response": 1,
                "q3_response": 1,
                "q4_response": 1,
                "q5_response": 1,
                "q6_response": 1,
                "n1": 600,
                "n2": 0,
                "n3": 0,
                "plot_x": 100,
                "plot_y": 0,
                "browser": "string",
                "source": "test"
            }
        }