from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_session
from .. import tables
from ..models.test import BaseTest, Test
import datetime


class TestService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def create(self, user_id: int, course_id: int, test_data: BaseTest) -> Test:
        test = tables.Test(**dict(course_id=test_data.course_id, name=test_data.name, creation_time=datetime.datetime.now()))
        self.session.add(test)
        self.session.commit()

        query = self.session.query(tables.Test)
        query = query.filter_by(course_id=test_data.course_id)
        tests = query.all()
        test_id = tests[-1].id

        for question in test_data.questions:
            question_row = tables.Questions(**dict(test_id=test_id, question=question.question))
            self.session.add(question_row)
            self.session.commit()

            for answer in question.answers:
                query = self.session.query(tables.Questions)
                query = query.filter_by(test_id=test_id)
                questions = query.all()
                answer_dict = dict(question_id=questions[-1].id,
                                   answer=answer,
                                   is_right=(answer in question.rightAnswers))
                answer_row = tables.Answers(**answer_dict)
                self.session.add(answer_row)
                self.session.commit()
        test: Test = Test.create(test, test_id, test_data.course_id, test_data.name, test_data.creation_time, test_data.questions)
        return test
