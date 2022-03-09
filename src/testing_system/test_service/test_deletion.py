from fastapi import Depends
from testing_system.test_service.search_engine import TestSearchingService
from sqlalchemy.orm import Session
from ..database import get_session
from sqlalchemy import select
from .. import tables


class TestDeletionService(TestSearchingService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_test(self, test_id: int) -> tables.Test:
        statement = select(tables.Test).filter_by(id=test_id)
        return self.session.execute(statement).scalars().first()

    def delete_test(self, test_id: int):
        test_row = self.get_test(test_id)
        self.session.delete(test_row)
        self.session.commit()

    def delete_answers(self, question_id: int):
        for answer in self.get_answers(question_id):
            self.session.delete(answer)
            self.session.commit()

    def delete(self, user_id: int, course_id: int, test_id: int):
        self.check_accessibility(user_id, course_id)
        self.delete_test(test_id)
        for question in self.get_questions(test_id):
            self.delete_answers(question.id)
            self.session.delete(question)
            self.session.commit()