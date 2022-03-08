from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import tables, constants
from ..database import get_session
from sqlalchemy import select


class BaseTestService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_tests_by_course_id(self, course_id: int) -> List[tables.Test]:
        query = self.session.query(tables.Test)
        query = query.filter_by(course_id=course_id)
        tests = query.all()
        return tests

    def get_course_ids(self, user_id: int) -> List[int]:
        statement = select(tables.Participants.course_id).filter_by(user_id=user_id)
        return self.session.execute(statement).scalars().all()

    def check_accessibility(self, user_id: int, course_id: int):
        if course_id not in self.get_course_ids(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)
