from typing import List, Optional
from pydantic import BaseModel
from datetime import date


class BaseAnswer(BaseModel):
    answer: str
    is_right: Optional[bool]


class BaseQuestion(BaseModel):
    question: str
    answers: List[BaseAnswer]


class BaseTest(BaseModel):
    course_id: int
    name: str
    creation_time: date
    questions: List[BaseQuestion]