from typing import List

from fastapi import APIRouter, Depends

from testing_system.models.auth import User
from testing_system.models.course import Course, CourseCreate, BaseCourse, CourseUpdate
from testing_system.services.auth import get_current_user
from testing_system.services.course import CourseService

router = APIRouter(prefix='/courses')


@router.get('/', response_model=List[Course])
def get_courses(user: User = Depends(get_current_user), service: CourseService = Depends()):
    return service.get_courses(user.id)


@router.post('/', response_model=Course)
def create_course(course_data: BaseCourse, user: User = Depends(get_current_user), service: CourseService = Depends()):
    return service.create(user.id, course_data)


@router.get('/{course_id}', response_model=Course)
def get_course(course_id: int, user: User = Depends(get_current_user), service: CourseService = Depends()):
    return service.get(user.id, course_id)


@router.put('/{course_id}', response_model=Course)
def update_course(
        course_id: int,
        course_data: CourseUpdate,
        service: CourseService = Depends(),
        user: User = Depends(get_current_user)):
    return service.update(user.id, course_id, course_data)
