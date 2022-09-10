from typing import List

from fastapi import Depends
from sqlalchemy import select
from .. import tables
from testing_system.database import get_session
from testing_system.test_service.base_test_service import BaseTestService
from sqlalchemy.orm import Session

from ..models.test_results import TestResults


class TestResultsService(BaseTestService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_results_from_table(self, test_id: int) -> List[tables.Results]:
        statement = select(tables.Results).filter_by(test_id=test_id)
        return self.session.execute(statement).scalars().all()

    def get_results(self, user_id: int, course_id: int, test_id: int, course_owner_id: int) -> TestResults:
        self.check_for_moderator_rights(user_id, course_id, course_owner_id)
        test_result_rows = self.get_results_from_table(test_id)
        if not test_result_rows:
            return TestResults(max_score=0, results=[])
        max_score = test_result_rows[0].max_score
        query = self.session.query(
            tables.Results.user_id, tables.User.username.label("user_name"),
            tables.User.email.label("user_email"), tables.Results.score
        ).join(tables.Results).filter(tables.Results.test_id == test_id).all()
        test_result = TestResults(max_score=max_score, results=query)
        return test_result
