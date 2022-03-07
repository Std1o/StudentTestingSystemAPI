from typing import List

from pydantic import BaseModel
from datetime import date


class BaseQuestion(BaseModel):
    question: str
    answers: List[str]
    rightAnswers: List[str]


class BaseTest(BaseModel):
    course_id: int
    name: str
    creation_time: date
    questions: List[BaseQuestion]

    class Config:
        orm_mode = True


class Question(BaseQuestion):
    id: int

    class Config:
        orm_mode = True


class Test(BaseTest):
    id: int

    def create(self, id: int, course_id: int, name: str, creation_time: date, questions: List[BaseQuestion]):
        self.id = id
        self.course_id = course_id
        self.name = name
        self.creation_time = creation_time
        self.questions = questions
        return self

    class Config:
        orm_mode = True