import enum
from sqlite3 import Date
from typing import List
from pydantic import BaseModel


class Rating(BaseModel):
    user_id: int
    username: str
    email: str
    score: float
    max_score: int
    passing_time: Date


class TestResults(BaseModel):
    results: List[Rating]
    max_score: int


class OrderingEnum(enum.Enum):
    SCORE = "SCORE"
    SCORE_DESC = "SCORE_DESC"
    DATE = "DATE"
    DATE_DESC = "DATE_DESC"
