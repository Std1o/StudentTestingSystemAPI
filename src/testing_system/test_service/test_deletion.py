from typing import List

from fastapi import Depends
from testing_system.test_service.test_getter import TestSearchingService
from sqlalchemy.orm import Session
from ..database import get_session
from sqlalchemy import select
from .. import tables


class TestDeletionService(TestSearchingService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    # getters
    def get_test(self, test_id: int) -> tables.Test:
        statement = select(tables.Test).filter_by(id=test_id)
        return self.session.execute(statement).scalars().first()

    def get_users_answers(self, answer_id: int) -> List[tables.UsersAnswers]:
        statement = select(tables.UsersAnswers).filter_by(answer_id=answer_id)
        return self.session.execute(statement).scalars().all()

    def get_questions_results(self, question_id: int) -> List[tables.QuestionsResults]:
        statement = select(tables.QuestionsResults).filter_by(question_id=question_id)
        return self.session.execute(statement).scalars().all()

    def get_test_results(self, test_id: int) -> List[tables.Results]:
        statement = select(tables.Results).filter_by(test_id=test_id)
        return self.session.execute(statement).scalars().all()

    # results deletion
    def delete_test_results(self, test_id: int):
        for test_result in self.get_test_results(test_id):
            self.session.delete(test_result)
            self.session.commit()

    def delete_users_answers(self, answer_id: int):
        for user_answer in self.get_users_answers(answer_id):
            self.session.delete(user_answer)
            self.session.commit()

    def delete_questions_results(self, question_id: int):
        for question_result in self.get_questions_results(question_id):
            self.session.delete(question_result)
            self.session.commit()

    # deletion

    def delete_test(self, test_id: int):
        test_row = self.get_test(test_id)
        self.session.delete(test_row)
        self.session.commit()
        self.delete_test_results(test_id)

    def delete_answers(self, question_id: int):
        for answer in self.get_answers(question_id):
            self.session.delete(answer)
            self.session.commit()
            self.delete_users_answers(answer.id)

    def delete_questions(self, test_id: int):
        for question in self.get_questions(test_id):
            self.delete_answers(question.id)
            self.session.delete(question)
            self.session.commit()
            self.delete_questions_results(question.id)

    # main functions

    def delete(self, user_id: int, course_id: int, test_id: int):
        self.check_for_moderator_rights(user_id, course_id)
        self.delete_test(test_id)
        self.delete_questions(test_id)

    def delete_all_course_tests(self, user_id: int, course_id: int):
        self.check_for_moderator_rights(user_id, course_id)
        for test in self.get_tests_by_course_id(course_id):
            self.delete(user_id, course_id, test.id)
