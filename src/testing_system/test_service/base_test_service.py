from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import constants
from ..database import get_list
from ..models import tables
from ..services.base_course_service import get_participant


class BaseTestService:

    def get_tests_by_course_id(self, course_id: int) -> List[tables.Test]:
        return get_list("SELECT * FROM tests where course_id=%s", tables.Test, (course_id,))

    def get_course_ids(self, user_id: int) -> List[int]:
        course_ids = get_list("SELECT course_id FROM participants where user_id=%s", int, (user_id,))
        return course_ids

    def check_accessibility(self, user_id: int, course_id: int):
        if course_id not in self.get_course_ids(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)

    def check_for_moderator_rights(self, user_id: int, course_id: int):
        participant = get_participant(user_id, course_id)
        if not participant or (not participant.is_moderator and not participant.is_owner):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="This action is available only to moderators and the administrator")