from typing import List

from fastapi import Depends
from sqlalchemy import select
from .. import tables
from testing_system.database import get_session
from testing_system.test_service.base_test_service import BaseTestService
from sqlalchemy.orm import Session

from ..models.test_results import TestResults, TestResultsItem


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
        results: List[TestResultsItem] = []
        for test_result_row in test_result_rows:
            user = self.get_user_by_id(test_result_row.user_id)
            result_item = TestResultsItem(user_id=test_result_row.user_id,
                                          user_name=user.username,
                                          user_email=user.email,
                                          score=test_result_row.score)
            results.append(result_item)
            pass
        test_result = TestResults(max_score=max_score, results=results)
        return test_result
