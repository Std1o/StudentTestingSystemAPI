from typing import List, Optional

from pydantic import BaseModel
from datetime import date

from testing_system.models.test_creation import BaseAnswer, BaseQuestion, BaseTest


class Answer(BaseAnswer):
    id: int

    class Config:
        orm_mode = True


class Question(BaseQuestion):
    id: int
    answers: List[Answer]

    class Config:
        orm_mode = True


class Test(BaseTest):
    id: int
    questions: List[Question]

    class Config:
        orm_mode = True
