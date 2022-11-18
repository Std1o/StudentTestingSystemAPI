from typing import List
from pydantic import BaseModel

from testing_system.models.tables import Rating


class TestResults(BaseModel):
    results: List[Rating]
    max_score: int
