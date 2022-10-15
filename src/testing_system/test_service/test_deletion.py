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

    def get_test(self, test_id: int) -> tables.Test:
        statement = select(tables.Test).filter_by(id=test_id)
        return self.session.execute(statement).scalars().first()

    def delete(self, user_id: int, course_id: int, test_id: int):
        self.check_for_moderator_rights(user_id, course_id)
        test_row = self.get_test(test_id)
        self.session.delete(test_row)
        self.session.commit()
