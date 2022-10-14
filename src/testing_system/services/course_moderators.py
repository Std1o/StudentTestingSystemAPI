from fastapi import Depends, HTTPException, status

from .base_course_service import BaseCourseService
from .. import constants
from sqlalchemy.orm import Session
from ..database import get_session
from sqlalchemy import select
from .. import tables


def check_accessibility_by_owner_id(user_id, course_owner_id: int):
    if course_owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)


class CourseModeratorsService(BaseCourseService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_participant(self, moderator_id: int, course_id) -> tables.Participants:
        statement = select(tables.Participants).filter_by(user_id=moderator_id, course_id=course_id)
        return self.session.execute(statement).scalars().first()

    # main functions
    def add_moderator(self, user_id: int, course_owner_id: int, moderator_id: int, course_id: int):
        check_accessibility_by_owner_id(user_id, course_owner_id)
        participant = self.get_participant(moderator_id, course_id)
        if participant.is_moderator:
            raise HTTPException(status_code=418, detail="The user is already moderator")
        participant.is_moderator = True
        self.session.commit()
        return self.get_moderators(course_id)

    def delete_moderator(self, user_id: int, course_owner_id: int, moderator_id: int, course_id: int):
        check_accessibility_by_owner_id(user_id, course_owner_id)
        participant = self.get_participant(moderator_id, course_id)
        if not participant.is_moderator:
            raise HTTPException(status_code=418, detail="The user is not moderator")
        participant.is_moderator = False
        self.session.commit()
        return self.get_moderators(course_id)
