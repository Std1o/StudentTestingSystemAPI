from typing import List
from pydantic import BaseModel


class TestResultsItem(BaseModel):
    user_id: int
    username: str
    email: str
    score: float


class TestResults(BaseModel):
    results: List[TestResultsItem]
    max_score: int
