from typing import List
from fastapi import HTTPException, status
from .base_test_service import BaseTestService
from ..models import tables
from ..database import make_query, get_list
from ..models.test import Test, Answer, Question


class TestSearchingService(BaseTestService):

    def get_questions(self, test_id: int) -> List[tables.Questions]:
        return get_list("SELECT * FROM questions where test_id=?", tables.Questions, test_id)

    def get_answers(self, question_id: int) -> List[tables.Answers]:
        return get_list("SELECT * FROM answers where question_id=?", tables.Answers, question_id)

    def convert_test_from_table(self, test: tables.Test, show_right_ans: bool) -> Test:
        test_dict = dict(test)
        test_dict["questions"] = []
        test = Test(**test_dict)
        for question_row in self.get_questions(test.id):
            answers: List[Answer] = []
            for ans in self.get_answers(question_row.id):
                is_right = ans.is_right if show_right_ans else None
                answers.append(Answer(id=ans.id, answer=ans.answer, is_right=is_right))
            question = Question(id=question_row.id,
                                question=question_row.question,
                                answers=answers)
            test.questions.append(question)
        return test

    def get_tests(self, user_id: int, course_id: int) -> List[Test]:
        self.check_accessibility(user_id, course_id)
        tests = []
        for test in self.get_tests_by_course_id(course_id):
            tests.append(self.convert_test_from_table(test, False))
        return tests

    def get(self, user_id: int, course_id: int, test_id: int, for_result: bool) -> Test:
        self.check_accessibility(user_id, course_id)
        test = make_query("SELECT * FROM tests where id=? LIMIT 1", tables.Test, test_id)
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return self.convert_test_from_table(test, for_result)
