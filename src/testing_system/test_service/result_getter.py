from fastapi import Depends

from testing_system.test_service.base_test_service import BaseTestService
from sqlalchemy.orm import Session
from .. import tables, constants
from ..database import get_session


class TestResultService(BaseTestService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_result(self, user_id: int, test_id: int):
        pass