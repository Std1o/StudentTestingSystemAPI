from testing_system.test_service.test_getter import TestSearchingService
from ..database import make_query


class TestDeletionService(TestSearchingService):

    def delete(self, user_id: int, course_id: int, test_id: int):
        self.check_for_moderator_rights(user_id, course_id)
        make_query("DELETE FROM tests WHERE id = ?", None, test_id)
