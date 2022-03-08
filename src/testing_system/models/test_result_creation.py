from typing import List, Optional
from pydantic import BaseModel


class AnswerResultCreation(BaseModel):
    answer_id: int
    is_selected: bool


class QuestionResultCreation(BaseModel):
    question_id: int
    answers: List[AnswerResultCreation]


class TestResultCreation(BaseModel):
    test_id: int
