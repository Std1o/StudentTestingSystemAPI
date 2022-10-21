from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .base_test_service import BaseTestService
from ..database import get_session, make_query, insert_and_get_id
from ..models.test_creation import BaseTest, BaseQuestion, BaseAnswer
from .. import tables
import datetime


class TestCreationService(BaseTestService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def create_test(self, test_data: BaseTest):
        test = tables.Test(**dict(course_id=test_data.course_id,
                                  name=test_data.name,
                                  creation_time=datetime.datetime.now().strftime("%Y-%m-%d")))
        query = "INSERT INTO tests (course_id, name, creation_time) " \
                "VALUES (?, ?, ?)"
        test.id = insert_and_get_id(query, test.course_id, test.name, test.creation_time)
        return test

    def get_last_test_id(self, test_data: BaseTest):
        tests = self.get_tests_by_course_id(test_data.course_id)
        return tests[-1].id

    def create_question(self, test_id: int, question_data: BaseQuestion):
        question = tables.Questions(**dict(test_id=test_id, question=question_data.question))
        query = "INSERT INTO questions (test_id, question) " \
                "VALUES (?, ?)"
        question.id = insert_and_get_id(query, test_id, question.question)
        return question

    def get_last_question_id(self, test_id: int):
        query = self.session.query(tables.Questions)
        query = query.filter_by(test_id=test_id)
        questions = query.all()
        return questions[-1].id

    def create_answer(self, question_id: int, answer: BaseAnswer):
        query = "INSERT INTO answers (question_id, answer, is_right) " \
                "VALUES (?, ?, ?)"
        make_query(query, None, question_id, answer.answer, answer.is_right)

    def create(self, user_id: int, test_data: BaseTest):
        self.check_for_moderator_rights(user_id, test_data.course_id)
        test = self.create_test(test_data)
        for question_data in test_data.questions:
            question = self.create_question(test.id, question_data)
            for answer in question_data.answers:
                self.create_answer(question.id, answer)
        return test.id
