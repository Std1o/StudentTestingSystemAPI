from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .base_test_service import BaseTestService
from .. import constants
from ..database import get_session
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
                                  creation_time=datetime.datetime.now()))
        self.session.add(test)
        self.session.commit()
        return test

    def get_last_test_id(self, test_data: BaseTest):
        tests = self.get_tests_by_course_id(test_data.course_id)
        return tests[-1].id

    def create_question(self, test_id: int, question: BaseQuestion):
        question_row = tables.Questions(**dict(test_id=test_id, question=question.question))
        self.session.add(question_row)
        self.session.commit()

    def get_last_question_id(self, test_id: int):
        query = self.session.query(tables.Questions)
        query = query.filter_by(test_id=test_id)
        questions = query.all()
        return questions[-1].id

    def create_answer(self, test_id: int, answer: BaseAnswer):
        answer_dict = answer.dict()
        answer_dict['question_id'] = self.get_last_question_id(test_id)
        answer_row = tables.Answers(**answer_dict)
        self.session.add(answer_row)
        self.session.commit()

    def create(self, user_id: int, course_owner_id: int, test_data: BaseTest):
        if course_owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)
        self.create_test(test_data)
        test_id = self.get_last_test_id(test_data)
        for question in test_data.questions:
            self.create_question(test_id, question)
            for answer in question.answers:
                self.create_answer(test_id, answer)
        return test_id
