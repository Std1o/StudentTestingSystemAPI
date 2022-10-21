from sqlite3 import Date

from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    username: str
    password_hash: str

    class Config:
        orm_mode = True

class Course(BaseModel):
    id: int
    name: str
    course_code: str
    img: str

    class Config:
        orm_mode = True


class Participants(BaseModel):
    user_id: int
    course_id: int
    is_moderator: bool
    is_owner: bool


class Test(BaseModel):
    id: int
    course_id: int
    name: str
    creation_time: Date

    class Config:
        orm_mode = True


class Questions(BaseModel):
    id: int
    test_id: int
    question: str


class Answers(BaseModel):
    id: int
    question_id: int
    answer: str
    is_right: bool


class UsersAnswers(BaseModel):
    id: int
    user_id: int
    answer_id: int
    is_selected: bool


class QuestionsResults(BaseModel):
    id: int
    user_id: int
    question_id: int
    score: float


class Results(BaseModel):
    id: int
    user_id: int
    test_id: int
    max_score: int
    score: float
