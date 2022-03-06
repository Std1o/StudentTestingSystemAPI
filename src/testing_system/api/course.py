from typing import List

from fastapi import APIRouter, Depends

from testing_system.models.auth import User
from testing_system.models.course import Course, CourseCreate, BaseCourse
from testing_system.services.auth import get_current_user
from testing_system.services.course import CourseService

router = APIRouter(prefix='/courses')

@router.get('/', response_model=List[Course])
def get_courses(user: User = Depends(get_current_user), service: CourseService = Depends()):
    return service.get_courses(user.id)

@router.post('/', response_model=Course)
def create_course(course_data: BaseCourse, user: User = Depends(get_current_user), service: CourseService = Depends()):
    return service.create(user.id, course_data)