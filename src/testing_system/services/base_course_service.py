from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from ..database import get_session
from typing import List
from sqlalchemy import select
from .. import tables


class BaseCourseService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_moderators_ids(self, course_id: int) -> List[int]:
        statement = select(tables.Participants.user_id).filter_by(course_id=course_id, is_moderator=True)
        return self.session.execute(statement).scalars().all()

    def get_moderators(self, course_id: int) -> List[tables.User]:
        moderators_ids = self.get_moderators_ids(course_id)
        users: List[tables.User] = []
        for user_id in moderators_ids:
            user = self.session.query(tables.User).filter_by(id=user_id).first()
            users.append(user)
        return users
