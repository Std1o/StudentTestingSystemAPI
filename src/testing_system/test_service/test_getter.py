from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from .base_test_service import BaseTestService
from .. import tables
from ..database import get_session
from ..models.test import Test, Answer, Question


class TestSearchingService(BaseTestService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_questions(self, test_id: int) -> List[tables.Questions]:
        statement = select(tables.Questions).filter_by(test_id=test_id)
        return self.session.execute(statement).scalars().all()

    def get_answers(self, question_id: int) -> List[tables.Answers]:
        statement = select(tables.Answers).filter_by(question_id=question_id)
        return self.session.execute(statement).scalars().all()

    def convert_test_from_table(self, test: tables.Test, show_right_ans: bool) -> Test:
        test: Test = test
        test.questions = []
        for question_row in self.get_questions(test.id):
            answers: List[Answer] = []
            for ans in self.get_answers(question_row.id):
                is_right = ans.is_right if show_right_ans else None
                answers.append(Answer(id=ans.id, answer=ans.answer, is_right=is_right))
            question = Question(id=question_row.id,
                                question=question_row.question,
                                answers=answers)
            test.questions.append(question)
        return test

    def get_tests(self, user_id: int, course_id: int) -> List[Test]:
        self.check_accessibility(user_id, course_id)
        tests = []
        for test in self.get_tests_by_course_id(course_id):
            tests.append(self.convert_test_from_table(test, False))
        return tests

    def get(self, user_id: int, course_id: int, test_id: int, for_result: bool) -> Test:
        self.check_accessibility(user_id, course_id)
        statement = select(tables.Test).filter_by(id=test_id)
        test = self.session.execute(statement).scalars().first()
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return self.convert_test_from_table(test, for_result)
