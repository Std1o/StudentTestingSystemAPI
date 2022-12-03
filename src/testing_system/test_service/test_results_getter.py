from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from testing_system.database import get_list
from testing_system.test_service.base_test_service import BaseTestService
from sqlalchemy.orm import Session
from sqlite3 import Date

from ..models import tables
from ..models.test_results import TestResults, OrderingEnum


class TestResultsService(BaseTestService):

    def get_results_from_table(self, test_id: int, only_max_result: bool = None,
                               search_prefix: str = None,
                               upper_bound: float = None, lower_bound: float = None, score_equals: float = None,
                               date_from: Date = None, date_to: Date = None,
                               ordering: Optional[OrderingEnum] = None) -> List[tables.Results]:
        query = f"SELECT * from rating_view WHERE test_id={test_id}"
        if only_max_result:
            query += " AND score=max_score"
        if search_prefix:
            query += f" AND ((lower(username) LIKE '%{search_prefix}%') OR (lower(email) LIKE '%{search_prefix}%'))"
        if date_from and date_to:
            query += f" AND passing_time BETWEEN '{date_from}' AND '{date_to}'"
        if date_from and not date_to:
            query += f" AND passing_time BETWEEN '{date_from}' AND '{date_from}'"
        if date_to and not date_from:
            query += f" AND passing_time BETWEEN '{date_to}' AND '{date_to}'"
        if upper_bound:
            query += f" AND score < {upper_bound}"
        if lower_bound:
            query += f" AND score > {lower_bound}"
        if score_equals:
            query += f" AND score = {score_equals}"

        # ORDERING
        if ordering == OrderingEnum.SCORE:
            query += " ORDER BY score"
        elif ordering == OrderingEnum.SCORE_DESC:
            query += " ORDER BY score desc"
        elif ordering == OrderingEnum.DATE:
            query += " ORDER BY passing_time"
        elif ordering == OrderingEnum.DATE_DESC:
            query += " ORDER BY passing_time desc"

        query += ";"
        return get_list(query, tables.Rating)

    def get_results(self, user_id: int, course_id: int, test_id: int,
                    only_max_result: bool = None,
                    search_prefix: str = None,
                    upper_bound: float = None, lower_bound: float = None, score_equals: float = None,
                    date_from: Date = None, date_to: Date = None,
                    ordering: Optional[OrderingEnum] = None) -> TestResults:
        self.check_for_moderator_rights(user_id, course_id)
        test_result_rows = self.get_results_from_table(
            test_id, only_max_result, search_prefix,
            upper_bound, lower_bound, score_equals,
            date_from, date_to, ordering
        )
        if not test_result_rows:
            return TestResults(max_score=0, results=[])
        max_score = test_result_rows[0].max_score
        test_result = TestResults(max_score=max_score, results=test_result_rows)
        return test_result
