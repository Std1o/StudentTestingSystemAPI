from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

from .. import tables
from ..database import get_session
from ..models.course import CourseCreate, Participants, BaseCourse


class CourseService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_course_ids(self, user_id: int) -> List[int]:
        statement = select(tables.Participants.course_id).filter_by(user_id=user_id)
        return self.session.execute(statement).scalars().all()

    def get_courses(self, user_id: int) -> List[tables.Course]:
        query = self.session.query(tables.Course)
        query = query.filter(tables.Course.id.in_(self.get_course_ids(user_id)))
        courses = query.all()
        return courses

    def create(self, user_id: int, course_data: BaseCourse) -> tables.Course:
        course_dict = course_data.dict()
        course_dict['img'] = 'placeholder'
        course_dict['owner_id'] = user_id
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
        return course

    def _get(self, user_id: int, course_id: int) -> tables.Course:
        query = self.session.query(tables.Course)
        query = query.filter(tables.Course.id.in_(self.get_course_ids(user_id)))
        course = query.filter_by(id=course_id).first()
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return course

    def get(self, user_id: int, course_id: int) -> tables.Operation:
        return self._get(user_id, course_id)

    def update(self, user_id: int, course_id: int, course_data: BaseCourse) -> tables.Course:
        course = self._get(user_id, course_id)
        for field, value in course_data:
            setattr(course, field, value)
        self.session.commit()
        return course
