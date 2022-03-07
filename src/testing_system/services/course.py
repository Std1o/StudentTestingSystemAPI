from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import constants

from .. import tables
from ..database import get_session
from ..models.course import CourseCreate, Participants, BaseCourse, Course


class CourseService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_course_ids(self, user_id: int) -> List[int]:
        statement = select(tables.Participants.course_id).filter_by(user_id=user_id)
        return self.session.execute(statement).scalars().all()

    def get_participants_ids(self, course_id: int) -> List[int]:
        statement = select(tables.Participants.user_id).filter_by(course_id=course_id)
        return self.session.execute(statement).scalars().all()

    def get_participants(self, course_id: int) -> List[tables.User]:
        participants_ids = self.get_participants_ids(course_id)
        users: List[tables.User] = []
        for user_id in participants_ids:
            user = self.session.query(tables.User).filter_by(id=user_id).first()
            users.append(user)
        return users

    def get_courses(self, user_id: int) -> List[Course]:
        query = self.session.query(tables.Course)
        query = query.filter(tables.Course.id.in_(self.get_course_ids(user_id)))

        courses = []
        for course_row in query.all():
            course: Course = course_row
            course.participants = self.get_participants(course.id)
            courses.append(course)
        return courses

    def create(self, user_id: int, course_data: BaseCourse) -> Course:
        course_dict = course_data.dict()
        course_dict['img'] = 'placeholder'
        course_dict['owner_id'] = user_id
        course_dict['course_code'] = 'placeholder'
        course_creator = CourseCreate(**course_dict)
        course = tables.Course(**course_creator.dict())
        self.session.add(course)
        self.session.commit()

        query = self.session.query(tables.Course)
        query = query.filter_by(owner_id=course_dict['owner_id'])
        courses = query.all()
        participants = Participants(user_id=course_dict['owner_id'], course_id=courses[-1].id)
        self.session.add(tables.Participants(**participants.dict()))
        self.session.commit()
        course: Course = course
        course.participants = self.get_participants(course.id)
        return course

    def _get(self, user_id: int, course_id: int) -> Course:
        query = self.session.query(tables.Course)
        query = query.filter(tables.Course.id.in_(self.get_course_ids(user_id)))
        course = query.filter_by(id=course_id).first()
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        course: Course = course
        course.participants = self.get_participants(course.id)
        return course

    def get(self, user_id: int, course_id: int) -> Course:
        return self._get(user_id, course_id)

    def update(self, user_id: int, course_id: int, course_data: BaseCourse) -> Course:
        course = self._get(user_id, course_id)
        if course.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)
        for field, value in course_data:
            setattr(course, field, value)
        self.session.commit()
        return course

    def delete(self, user_id: int, course_id: int):
        course = self._get(user_id, course_id)
        if course.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)
        self.session.delete(course)
        self.session.commit()

    def join(self, user_id: int, course_id) -> Course:
        if user_id in self.get_participants_ids(course_id):
            raise HTTPException(status_code=418, detail="You have already joined the course")
        participants = Participants(user_id=user_id, course_id=course_id)
        self.session.add(tables.Participants(**participants.dict()))
        self.session.commit()
        return self._get(user_id, course_id)
