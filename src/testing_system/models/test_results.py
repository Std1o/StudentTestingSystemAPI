from typing import List
from pydantic import BaseModel


class TestResultsItem(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    score: float


class TestResults(BaseModel):
    results: List[TestResultsItem]
    max_score: int
