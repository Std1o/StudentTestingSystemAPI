from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base_course_service import BaseCourseService
from .. import constants
import random
from .. import tables
from ..database import get_session
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
        statement = select(tables.Participants.user_id).filter_by(course_id=course_id)
        return self.session.execute(statement).scalars().all()

    def get_participants_from_table(self, course_id: int) -> List[tables.Participants]:
        statement = select(tables.Participants).filter_by(course_id=course_id)
        return self.session.execute(statement).scalars().all()

    def get_course_by_code(self, course_code: str) -> tables.Course:
        statement = select(tables.Course).filter_by(course_code=course_code)
        return self.session.execute(statement).scalars().first()

    def get_participant(self, participant_id: int, course_id) -> tables.Participants:
        statement = select(tables.Participants).filter_by(user_id=participant_id, course_id=course_id)
        return self.session.execute(statement).scalars().first()

    def get_courses(self, user_id: int) -> List[Course]:
        courses = self.session.query(tables.Course).join(tables.Participants).filter(
            tables.Course.id == tables.Participants.course_id,
            tables.Participants.user_id == user_id
        ).all()
        print(courses)
        for course in courses:
            course.participants = self.get_participants(course.id)
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
        course = tables.Course(**course_creator.dict())
        self.session.add(course)
        self.session.commit()

        participant = Participants(user_id=user_id, course_id=course.id, is_owner=True)
        self.session.add(tables.Participants(**participant.dict()))
        self.session.commit()
        course: Course = course
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

    def delete_participants(self, course_id: int):
        for participant in self.get_participants_from_table(course_id):
            self.session.delete(participant)
            self.session.commit()

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
