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

    def get_courses(self, user_id: int) -> List[tables.Course]:
        statement = select(tables.Participants.course_id).filter_by(user_id=user_id)
        course_ids = self.session.execute(statement).scalars().all()
        query = self.session.query(tables.Course)
        query = query.filter(tables.Course.id.in_(course_ids))
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

    def last_row(self, Table: type):  # -> Table
        primary_key = inspect(Table).primary_key[0].name  # must be an arithmetic type
        primary_key_row = getattr(Table, primary_key)
        # get first, sorted by negative ID (primary key)
        return self.session.query(Table).order_by(-primary_key_row).first()
