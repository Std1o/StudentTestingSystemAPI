from fastapi import Depends, HTTPException, status

from .base_course_service import BaseCourseService
from .. import constants
from sqlalchemy.orm import Session
from ..database import get_session
from sqlalchemy import select
from .. import tables

class CourseModeratorsService(BaseCourseService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def check_accessibility(self, user_id, course_id: int):
        participant = self.get_participant(user_id, course_id)
        if not participant.is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)

    def get_participant(self, moderator_id: int, course_id) -> tables.Participants:
        statement = select(tables.Participants).filter_by(user_id=moderator_id, course_id=course_id)
        return self.session.execute(statement).scalars().first()

    # main functions
    def add_moderator(self, user_id: int, moderator_id: int, course_id: int):
        self.check_accessibility(user_id, course_id)
        participant = self.get_participant(moderator_id, course_id)
        if participant.is_moderator:
            raise HTTPException(status_code=418, detail="The user is already moderator")
        participant.is_moderator = True
        self.session.commit()
        return self.get_participants(course_id)

    def delete_moderator(self, user_id: int, moderator_id: int, course_id: int):
        self.check_accessibility(user_id, course_id)
        participant = self.get_participant(moderator_id, course_id)
        if not participant.is_moderator:
            raise HTTPException(status_code=418, detail="The user is not moderator")
        participant.is_moderator = False
        self.session.commit()
        return self.get_participants(course_id)
