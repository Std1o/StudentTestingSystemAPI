from typing import List

from fastapi import Depends
from sqlalchemy import select
from .. import tables
from testing_system.database import get_session, get_list
from testing_system.test_service.base_test_service import BaseTestService
from sqlalchemy.orm import Session

from ..models.test_results import TestResults, TestResultsItem


class TestResultsService(BaseTestService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_results_from_table(self, test_id: int, only_max_result: bool) -> List[tables.Results]:
        if only_max_result:
            results = get_list("SELECT * FROM results "
                               "WHERE test_id=? AND score=max_score", tables.Results, test_id)
        else:
            results = get_list("SELECT * FROM results "
                               "WHERE test_id=?", tables.Results, test_id)
        return results

    def get_results(self, user_id: int, course_id: int, test_id: int,
                    only_max_result: bool) -> TestResults:
        self.check_for_moderator_rights(user_id, course_id)
        test_result_rows = self.get_results_from_table(test_id, only_max_result)
        if not test_result_rows:
            return TestResults(max_score=0, results=[])
        max_score = test_result_rows[0].max_score
        results = get_list("SELECT user_id, username, email, score FROM users "
                           "INNER JOIN results r on users.id=user_id"
                           + f" AND r.test_id = {test_id}", TestResultsItem)
        test_result = TestResults(max_score=max_score, results=results)
        return test_result
