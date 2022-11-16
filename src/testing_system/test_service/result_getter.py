from typing import List

from fastapi import HTTPException, status
from .test_getter import TestSearchingService
from ..models import tables
from ..database import make_query
from ..models.test import Answer, Question
from ..models.test_result import TestResult, AnswerResult, QuestionResult


class TestResultService(TestSearchingService):

    def get_user_answer(self, answer_id: int, user_id: int) -> tables.UsersAnswers:
        return make_query("SELECT * FROM users_answers "
                          "where answer_id=%s AND user_id=%s", tables.UsersAnswers, (answer_id, user_id,))

    def get_answer_result(self, ans: Answer, user_id: int) -> AnswerResult:
        user_answer = self.get_user_answer(ans.id, user_id)
        if not user_answer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        answer = AnswerResult(is_selected=user_answer.is_selected,
                              id=ans.id,
                              answer=ans.answer,
                              is_right=ans.is_right)
        return answer

    def get_question_score(self, question_id: int, user_id: int) -> float:
        score = make_query("SELECT score FROM questions_results "
                           "where question_id =%s AND user_id=%s", float, (question_id, user_id,))
        return score

    def get_question_result(self, question: Question, answers: List[AnswerResult], user_id: int) -> QuestionResult:
        score = self.get_question_score(question.id, user_id)
        question_result = QuestionResult(answers=answers,
                                         score=score,
                                         id=question.id,
                                         question=question.question)
        return question_result

    def get_test_score(self, user_id: int, test_id: int) -> float:
        return make_query("SELECT score FROM results "
                          "where test_id = %s AND user_id= %s ", float, (test_id, user_id,))

    def get_result(self, user_id: int, course_id: int, test_id: int) -> TestResult:
        test = self.get(user_id, course_id, test_id, True)
        questions: List[QuestionResult] = []
        for question in test.questions:
            answers: List[AnswerResult] = []
            for ans in question.answers:
                answers.append(self.get_answer_result(ans, user_id))
            questions.append(self.get_question_result(question, answers, user_id))
        score = self.get_test_score(user_id, test_id)
        if score is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        test_result = TestResult(questions=questions,
                                 max_score=len(questions),
                                 score=score)
        return test_result
