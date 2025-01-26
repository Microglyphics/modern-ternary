from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal
import uuid

class SurveyResponse(BaseModel):
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    q1_response: Optional[int] = Field(None, ge=1, le=6)
    q2_response: Optional[int] = Field(None, ge=1, le=6)
    q3_response: Optional[int] = Field(None, ge=1, le=6)
    q4_response: Optional[int] = Field(None, ge=1, le=6)
    q5_response: Optional[int] = Field(None, ge=1, le=6)
    q6_response: Optional[int] = Field(None, ge=1, le=6)
    n1: Optional[int] = Field(None, ge=0, le=600)
    n2: Optional[int] = Field(None, ge=0, le=600)
    n3: Optional[int] = Field(None, ge=0, le=600)
    plot_x: Optional[Decimal] = Field(None, decimal_places=2)
    plot_y: Optional[Decimal] = Field(None, decimal_places=2)
    browser: Optional[str] = None
    region: Optional[str] = None
    source: str = "local"
    hash_email_session: Optional[str] = None

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
                "plot_x": "100.00",
                "plot_y": "0.00",
                "browser": "string",
                "region": "string",
                "source": "local"
            }
        }

class QuestionResponse(BaseModel):
    id: str
    text: str
    scores: list[float]

class Question(BaseModel):
    text: str
    responses: list[QuestionResponse]