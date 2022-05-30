from typing import List

from fastapi import APIRouter, Depends, Response, status

from testing_system.models.auth import User
from testing_system.models.course import Course, BaseCourse, CourseUpdate, Moderator
from testing_system.services.auth import get_current_user
from testing_system.services.course import CourseService
from testing_system.services.course_moderators import CourseModeratorsService
from testing_system.test_service.test_deletion import TestDeletionService

router = APIRouter(prefix='/course/moderators')


@router.post('/', response_model=Moderator)
def add_moderator(course_id: int, course_owner_id: int, moderator_id: int,
                  user: User = Depends(get_current_user), service: CourseModeratorsService = Depends()):
    return service.add_moderator(user.id, course_owner_id, moderator_id, course_id)


@router.delete('/', response_model=List[User])
def delete_moderator(course_id: int, course_owner_id: int, moderator_id: int,
                  user: User = Depends(get_current_user), service: CourseModeratorsService = Depends()):
    return service.delete_moderator(user.id, course_owner_id, moderator_id, course_id)
