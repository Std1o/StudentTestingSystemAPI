from sqlite3 import Date
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
                searching_service: TestSearchingService = Depends()):
    test_id = service.create(user.id, test_data)
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


@router.post('/demo_result/', response_model=TestResult)
def calculate_demo_result(course_id: int,
                          questions: List[QuestionResultCreation],
                          service: TestResultCalculatorService = Depends(),
                          user: User = Depends(get_current_user)):
    return service.calculate_demo_result(user.id, course_id, questions)


@router.delete('/{test_id}')
def delete_test(course_id: int, test_id: int, user: User = Depends(get_current_user),
                service: TestDeletionService = Depends()):
    service.delete(user.id, course_id, test_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/result/{test_id}', response_model=TestResult)
def get_result(course_id: int, test_id: int, user: User = Depends(get_current_user),
               service: TestResultService = Depends()):
    return service.get_result(user.id, course_id, test_id)


@router.get('/results/{test_id}', response_model=TestResults)
def get_results(course_id: int, test_id: int,
                only_max_result: bool = None,
                username: str = None, email: str = None,
                upper_bound: int = None, lower_bound: int = None, score_equals: int = None,
                date_from: Date = None, date_to: Date = None,
                order_by_score: bool = False, order_by_score_desc: bool = None,
                order_by_date: bool = False, order_by_date_desc: bool = None,
                user: User = Depends(get_current_user),
                service: TestResultsService = Depends()):
    return service.get_results(
        user.id, course_id, test_id, only_max_result, username, email,
        upper_bound, lower_bound, score_equals,
        date_from, date_to,
        order_by_score, order_by_score_desc,
        order_by_date, order_by_date_desc
    )
