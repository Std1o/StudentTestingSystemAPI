from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from ..database import get_session
from typing import List
from sqlalchemy import select
from .. import tables
from ..models.course import CourseUsers


class BaseCourseService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_participants(self, course_id: int) -> List[CourseUsers]:
        users = self.session.query(
            tables.User.email, tables.User.username, tables.User.id,
            tables.Participants.is_moderator, tables.Participants.is_owner
        ).join(tables.Participants).filter(
            tables.Participants.course_id == course_id
        ).all()
        return users
