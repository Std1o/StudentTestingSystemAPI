from typing import List
from fastapi import APIRouter, Depends, Response, status
from testing_system.models.test import Test, BaseTest
from testing_system.models.auth import User
from testing_system.models.test_result import TestResult
from testing_system.models.test_result_creation import QuestionResultCreation
from testing_system.models.test_results import TestResults
from testing_system.services.auth import get_current_user
from testing_system.services.course import CourseService
from testing_system.test_service.result_getter import TestResultService
from testing_system.test_service.test_getter import TestSearchingService
from testing_system.test_service.test_creation import TestCreationService
from testing_system.test_service.test_deletion import TestDeletionService
from testing_system.test_service.test_result_calculator import TestResultCalculatorService
from testing_system.test_service.test_results_getter import TestResultsService

router = APIRouter(prefix='/tests')


@router.post('/', response_model=Test)
def create_test(test_data: BaseTest,
                user: User = Depends(get_current_user),
                service: TestCreationService = Depends(),
                course_service: CourseService = Depends(),
                searching_service: TestSearchingService = Depends()):
    course_owner_id = course_service.get(user.id, test_data.course_id).owner_id
    test_id = service.create(user.id, course_owner_id, test_data)
    return searching_service.get(user.id, test_data.course_id, test_id, True)


@router.get('/', response_model=List[Test])
def get_tests(course_id: int, user: User = Depends(get_current_user), service: TestSearchingService = Depends()):
    return service.get_tests(user.id, course_id)


@router.get('/{test_id}', response_model=Test)
def get_test(course_id: int, test_id: int, user: User = Depends(get_current_user),
             service: TestSearchingService = Depends()):
    return service.get(user.id, course_id, test_id, False)


@router.post('/{test_id}')
def calculate_result(course_id: int,
                     test_id: int,
                     questions: List[QuestionResultCreation],
                     service: TestResultCalculatorService = Depends(),
                     user: User = Depends(get_current_user)):
    service.calculate_result(user.id, course_id, test_id, questions)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/{test_id}')
def delete_test(course_id: int, test_id: int, course_owner_id: int, user: User = Depends(get_current_user),
                service: TestDeletionService = Depends()):
    service.delete(user.id, course_id, test_id, course_owner_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/result/{test_id}', response_model=TestResult)
def get_result(course_id: int, test_id: int, user: User = Depends(get_current_user),
               service: TestResultService = Depends()):
    return service.get_result(user.id, course_id, test_id)


@router.get('/results/{test_id}', response_model=TestResults)
def get_results(course_id: int, test_id: int, course_owner_id: int, user: User = Depends(get_current_user),
                service: TestResultsService = Depends()):
    return service.get_results(user.id, course_id, test_id, course_owner_id)
