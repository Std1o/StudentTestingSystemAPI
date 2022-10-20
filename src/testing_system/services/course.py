from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base_course_service import BaseCourseService
from .. import constants
import random
from .. import tables
from ..database import get_session, make_query, get_list
from ..models.course import CourseCreate, Participants, BaseCourse, Course, CourseUsers


def generate_course_code() -> str:
    seq = "abcdefghijklmnopqrstuvwxyz0123456789"
    code = ''
    for i in range(0, 6):
        code += random.choice(seq)
    return code.upper()


class CourseService(BaseCourseService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def check_accessibility(self, user_id, course_id: int):
        participant = self.get_participant(user_id, course_id)
        if not participant.is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)

    def get_participants_ids(self, course_id: int) -> List[int]:
        participants = get_list("SELECT user_id FROM participants where course_id=?", int, course_id)
        return participants

    def get_course_by_code(self, course_code: str) -> Optional[Course]:
        course = make_query("SELECT * FROM courses where course_code=? LIMIT 1", course_code)
        if not course:
            return None
        return Course(**course)

    def get_participant(self, participant_id: int, course_id) -> tables.Participants:
        participant = make_query("SELECT * FROM participants "
                                 "where user_id=? AND course_id=? LIMIT 1", participant_id, course_id)
        return Participants(**participant)

    def get_courses(self, user_id: int) -> List[Course]:
        courses_dict_arr = get_list("SELECT id, name, course_code, img FROM courses "
                                    "INNER JOIN participants p on courses.id = p.course_id"
                                    + f" AND p.user_id = {user_id}", Course)
        courses = []
        for course in courses_dict_arr:
            course.participants = self.get_participants(course.id)
            courses.append(course)
        return courses

    def create(self, user_id: int, course_data: BaseCourse) -> Course:
        course_dict = course_data.dict()
        course_dict['img'] = 'placeholder'
        course_dict['course_code'] = generate_course_code()

        '''The probability that the code is already occupied is extremely small, 
        but if this happens, we generate a new code'''
        if self.get_course_by_code(course_dict['course_code']):
            course_dict['course_code'] = generate_course_code()
        course_creator = CourseCreate(**course_dict)
        query_course = "INSERT INTO courses (name, course_code, img) " \
                       "VALUES (" + f'"{course_creator.name}"' + "," \
                       + f'"{course_creator.course_code}"' + "," + f'"{course_creator.img}"'
        query_course += ");"
        make_query(query_course)
        course = self.get_course_by_code(course_creator.course_code)

        query = "INSERT INTO participants (user_id, course_id, is_moderator, is_owner) " \
                "VALUES (?, ?, ?, ?)"
        make_query(query, user_id, course.id, False, True)
        course.participants = self.get_participants(course.id)
        return course

    def _get(self, user_id: int, course_id: int) -> Course:
        course = self.session.query(tables.Course).join(tables.Participants).filter(
            tables.Course.id == course_id,
            tables.Participants.user_id == user_id
        ).first()
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        course.participants = self.get_participants(course.id)
        return course

    def get(self, user_id: int, course_id: int) -> Course:
        return self._get(user_id, course_id)

    def update(self, user_id: int, course_id: int, course_data: BaseCourse) -> Course:
        course = self._get(user_id, course_id)
        self.check_accessibility(user_id, course_id)
        for field, value in course_data:
            setattr(course, field, value)
        self.session.commit()
        return course

    def delete(self, user_id: int, course_id: int):
        self.check_accessibility(user_id, course_id)
        statement = select(tables.Course).filter_by(id=course_id)
        course = self.session.execute(statement).scalars().first()
        self.session.delete(course)
        self.session.commit()

    def join(self, user_id: int, course_code: str) -> Course:
        course = self.get_course_by_code(course_code)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        course_id = course.id
        if user_id in self.get_participants_ids(course_id):
            raise HTTPException(status_code=418, detail="You have already joined the course")
        participants = Participants(user_id=user_id, course_id=course_id)
        self.session.add(tables.Participants(**participants.dict()))
        self.session.commit()
        return self._get(user_id, course_id)

    def delete_participant(self, user_id: int, participant_id: int, course_id: int):
        self.check_accessibility(user_id, course_id)
        participant = self.get_participant(participant_id, course_id)
        self.session.delete(participant)
        self.session.commit()
        return self.get_participants(course_id)
