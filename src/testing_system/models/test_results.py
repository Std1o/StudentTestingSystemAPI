from typing import List
from pydantic import BaseModel
import enum

from testing_system.models.tables import Rating


class TestResults(BaseModel):
    results: List[Rating]
    max_score: int


class OrderingEnum(enum.Enum):
    SCORE = "SCORE"
    SCORE_DESC = "SCORE_DESC"
    DATE = "DATE"
    DATE_DESC = "DATE_DESC"
