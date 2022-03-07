from fastapi import APIRouter, Depends, Response, status
from testing_system.models.test import Test, BaseTest
from testing_system.models.auth import User
from testing_system.services.auth import get_current_user
from testing_system.services.test import TestService

router = APIRouter(prefix='/tests')


@router.post('/', response_model=Test)
def create_test(course_id: int,
                  test_data: BaseTest,
                  user: User = Depends(get_current_user),
                  service: TestService = Depends()):
    return service.create(user.id, course_id, test_data)
