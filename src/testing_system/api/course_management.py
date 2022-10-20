from typing import List
from fastapi import APIRouter, Depends
from testing_system.models.auth import User
from testing_system.models.course import CourseUsers
from testing_system.services.auth import get_current_user
from testing_system.services.course import CourseService

router = APIRouter(prefix='/course/management')


@router.delete('/participants', response_model=List[CourseUsers])
def delete_participant(course_id: int, participant_id: int,
                       user: User = Depends(get_current_user), service: CourseService = Depends()):
    return service.delete_participant(user.id, participant_id, course_id)
