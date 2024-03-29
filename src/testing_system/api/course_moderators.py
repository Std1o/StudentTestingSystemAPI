from typing import List

from fastapi import APIRouter, Depends

from testing_system.models.auth import User
from testing_system.models.course import CourseUsers
from testing_system.services.auth import get_current_user
from testing_system.services.course_moderators import CourseModeratorsService

router = APIRouter(prefix='/course/moderators')


@router.post('/', response_model=List[CourseUsers])
def add_moderator(course_id: int, moderator_id: int,
                  user: User = Depends(get_current_user), service: CourseModeratorsService = Depends()):
    return service.add_moderator(user.id, moderator_id, course_id)


@router.delete('/', response_model=List[CourseUsers])
def delete_moderator(course_id: int, moderator_id: int,
                  user: User = Depends(get_current_user), service: CourseModeratorsService = Depends()):
    return service.delete_moderator(user.id, moderator_id, course_id)
