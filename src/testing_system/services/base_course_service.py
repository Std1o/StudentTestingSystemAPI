from .. import constants
from ..database import get_list, make_query
from typing import List
from ..models.course import CourseUsers, Participants
from fastapi import HTTPException, status


def get_participants(course_id: int) -> List[CourseUsers]:
    users = get_list("SELECT email, username, user_id, is_moderator, is_owner "
                     "FROM users INNER JOIN participants p on users.id = p.user_id"
                     + f" WHERE p.course_id = {course_id}", CourseUsers)
    return users


def get_participant(participant_id: int, course_id) -> Participants:
    return make_query("SELECT * FROM participants "
                      "where user_id=%s AND course_id=%s LIMIT 1",
                      Participants, (participant_id, course_id,))


# is_course_owner
def check_accessibility(user_id, course_id: int):
    is_owner = make_query(f"SELECT isCourseOwner({user_id}, {course_id});", int)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)
