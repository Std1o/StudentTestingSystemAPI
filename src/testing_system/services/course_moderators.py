from fastapi import HTTPException
from .base_course_service import get_participant, get_participants, check_accessibility
from ..database import make_query


class CourseModeratorsService:

    def add_moderator(self, user_id: int, moderator_id: int, course_id: int):
        check_accessibility(user_id, course_id)
        participant = get_participant(moderator_id, course_id)
        if participant.is_moderator:
            raise HTTPException(status_code=418, detail="The user is already moderator")
        make_query("UPDATE participants SET is_moderator = ? "
                   "WHERE user_id = ? AND course_id = ?", None, True, moderator_id, course_id)
        return get_participants(course_id)

    def delete_moderator(self, user_id: int, moderator_id: int, course_id: int):
        check_accessibility(user_id, course_id)
        participant = get_participant(moderator_id, course_id)
        if not participant.is_moderator:
            raise HTTPException(status_code=418, detail="The user is not moderator")
        make_query("UPDATE participants SET is_moderator = ? "
                   "WHERE user_id = ? AND course_id = ?", None, False, moderator_id, course_id)
        return get_participants(course_id)
