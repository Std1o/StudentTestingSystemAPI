from fastapi import Depends, HTTPException, status

from .base_course_service import BaseCourseService
from .. import constants
from sqlalchemy.orm import Session
from ..database import get_session
from sqlalchemy import select
from .. import tables
from ..models.course import Moderator


def check_accessibility_by_owner_id(user_id, course_owner_id: int):
    if course_owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)


class CourseModeratorsService(BaseCourseService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_moderator(self, moderator_id: int, course_id) -> tables.Moderators:
        statement = select(tables.Moderators).filter_by(user_id=moderator_id, course_id=course_id)
        return self.session.execute(statement).scalars().first()

    # main functions
    def add_moderator(self, user_id: int, course_owner_id: int, moderator_id: int, course_id: int):
        check_accessibility_by_owner_id(user_id, course_owner_id)
        if moderator_id in self.get_moderators_ids(course_id):
            raise HTTPException(status_code=418, detail="The user is already moderator")
        moderator = Moderator(user_id=moderator_id, course_id=course_id)
        self.session.add(tables.Moderators(**moderator.dict()))
        self.session.commit()
        return moderator

    def delete_moderator(self, user_id: int, course_owner_id: int, moderator_id: int, course_id: int):
        check_accessibility_by_owner_id(user_id, course_owner_id)
        moderator = self.get_moderator(moderator_id, course_id)
        self.session.delete(moderator)
        self.session.commit()
        return self.get_moderators(course_id)
