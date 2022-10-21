from sqlalchemy.orm import Session
from fastapi import Depends
from ..database import get_session, get_list
from typing import List
from ..models.course import CourseUsers


class BaseCourseService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_participants(self, course_id: int) -> List[CourseUsers]:
        users = get_list("SELECT email, username, user_id, is_moderator, is_owner "
                         "FROM users INNER JOIN participants p on users.id = p.user_id"
                         + f" WHERE p.course_id = {course_id}", CourseUsers)
        return users
