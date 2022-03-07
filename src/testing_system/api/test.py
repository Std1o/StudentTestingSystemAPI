from fastapi import APIRouter, Depends, Response, status
from testing_system.models.test import Test, BaseTest
from testing_system.models.auth import User
from testing_system.services.auth import get_current_user
from testing_system.services.course import CourseService
from testing_system.services.test import TestService

router = APIRouter(prefix='/tests')


@router.post('/', response_model=Test)
def create_test(test_data: BaseTest,
                user: User = Depends(get_current_user),
                service: TestService = Depends(),
                course_service: CourseService = Depends()):
    course_owner_id = course_service.get(user.id, test_data.course_id).id
    return service.create(user.id, course_owner_id, test_data)
