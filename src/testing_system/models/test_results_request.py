from sqlite3 import Date
from typing import Optional

from pydantic import BaseModel

from testing_system.models.tables import Rating
from testing_system.models.test_results import OrderingEnum


class TestResultsRequest(BaseModel):
    only_max_result: bool = None
    search_prefix: str = None
    upper_bound: int = None
    lower_bound: int = None
    score_equals: int = None
    date_from: Date = None
    date_to: Date = None
    ordering: Optional[OrderingEnum] = None
