from typing import List
from testing_system.models.test import Answer, Question, Test


class AnswerResult(Answer):
    is_selected: bool

    class Config:
        orm_mode = True


class QuestionResult(Question):
    answers: List[AnswerResult]
    score: float

    class Config:
        orm_mode = True


class TestResult(Test):
    questions: List[QuestionResult]
    max_score: int
    score: float

    class Config:
        orm_mode = True
