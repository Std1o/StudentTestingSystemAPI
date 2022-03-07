from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_session
from .. import tables
from ..models.test import BaseTest, Test, BaseQuestion
import datetime


class TestService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def create_test(self, test_data: BaseTest):
        test = tables.Test(**dict(course_id=test_data.course_id,
                                  name=test_data.name,
                                  creation_time=datetime.datetime.now()))
        self.session.add(test)
        self.session.commit()
        return test

    def get_last_test_id(self, test_data: BaseTest):
        query = self.session.query(tables.Test)
        query = query.filter_by(course_id=test_data.course_id)
        tests = query.all()
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

    def create_answer(self, test_id: int, answer: str, question: BaseQuestion):
        question_id = self.get_last_question_id(test_id)
        answer_dict = dict(question_id=question_id,
                           answer=answer,
                           is_right=(answer in question.rightAnswers))
        answer_row = tables.Answers(**answer_dict)
        self.session.add(answer_row)
        self.session.commit()

    def create(self, test_data: BaseTest) -> Test:
        test = self.create_test(test_data)
        test_id = self.get_last_test_id(test_data)
        for question in test_data.questions:
            self.create_question(test_id, question)
            for answer in question.answers:
                self.create_answer(test_id, answer, question)
        test: Test = Test.create(test, test_id, test_data.course_id, test_data.name, test_data.creation_time,
                                 test_data.questions)
        return test
