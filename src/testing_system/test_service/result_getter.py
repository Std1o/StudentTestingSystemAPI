from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from .test_getter import TestSearchingService
from .. import tables
from ..database import get_session, make_query
from ..models.test import Answer, Question
from ..models.test_result import TestResult, AnswerResult, QuestionResult


class TestResultService(TestSearchingService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_user_answer(self, answer_id: int, user_id: int) -> tables.UsersAnswers:
        statement = select(tables.UsersAnswers).filter_by(answer_id=answer_id, user_id=user_id)
        return self.session.execute(statement).scalars().first()

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
        statement = select(tables.QuestionsResults.score).filter_by(question_id=question_id, user_id=user_id)
        return self.session.execute(statement).scalars().first()

    def get_question_result(self, question: Question, answers: List[AnswerResult], user_id: int) -> QuestionResult:
        question_result = QuestionResult(answers=answers,
                                         score=self.get_question_score(question.id, user_id),
                                         id=question.id,
                                         question=question.question)
        return question_result

    def get_test_score(self, user_id: int, test_id: int) -> float:
        return make_query("SELECT score FROM results "
                          "where test_id = ? AND user_id= ? ", int, test_id, user_id)

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
