from sqlite3 import Date
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select, func, or_, desc
from .. import tables
from testing_system.database import get_session
from testing_system.test_service.base_test_service import BaseTestService
from sqlalchemy.orm import Session

from ..models.test_results import TestResults, OrderingEnum, Rating


class TestResultsService(BaseTestService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_results_from_table(self, test_id: int, only_max_result: bool = None,
                               search_prefix: str = None,
                               upper_bound: float = None, lower_bound: float = None, score_equals: float = None,
                               date_from: Date = None, date_to: Date = None,
                               ordering: Optional[OrderingEnum] = None) -> List[Rating]:
        rating_query = self.session.query(
            tables.Results.user_id, tables.User.username, tables.User.email, tables.Results.score,
            tables.Results.max_score, tables.Results.test_id, tables.Results.passing_time
        ).join(tables.Participants).filter(
            tables.User.id == tables.Results.user_id,
            tables.Test.id == tables.Results.test_id,
            tables.Test.id == test_id
        )
        if only_max_result:
            rating_query = rating_query.filter(tables.Results.score == tables.Results.max_score)
        if search_prefix:
            rating_query = rating_query.filter(or_(tables.User.username.ilike(f"%{search_prefix}%"),
                                                   tables.User.email.ilike(f"%{search_prefix}%")))
        if date_from and date_to:
            rating_query = rating_query.filter(tables.Results.passing_time.between(date_from, date_to))
        if date_from and not date_to:
            rating_query = rating_query.filter(tables.Results.passing_time >= date_from)
        if date_to and not date_from:
            rating_query = rating_query.filter(tables.Results.passing_time >= date_to)
        if upper_bound:
            rating_query = rating_query.filter(tables.Results.score <= upper_bound)
        if lower_bound:
            rating_query = rating_query.filter(tables.Results.score >= lower_bound)
        if score_equals:
            rating_query = rating_query.filter(tables.Results.score == score_equals)

        # ORDERING
        if ordering == OrderingEnum.SCORE:
            rating_query = rating_query.order_by(tables.Results.score)
        elif ordering == OrderingEnum.SCORE_DESC:
            rating_query = rating_query.order_by(desc(tables.Results.score))
        elif ordering == OrderingEnum.DATE:
            rating_query = rating_query.order_by(tables.Results.passing_time)
        elif ordering == OrderingEnum.DATE_DESC:
            rating_query = rating_query.order_by(desc(tables.Results.passing_time))

        return rating_query.all()

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
