from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session

from .base_test_service import BaseTestService
from .. import tables
from ..database import get_session
from ..models.test_result import TestResult
from ..models.test_result_creation import QuestionResultCreation, AnswerResultCreation
from sqlalchemy import select


class TestResultCalculatorService(BaseTestService):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.session = session

    def get_answer(self, answer_id: int) -> tables.Answers:
        statement = select(tables.Answers).filter_by(id=answer_id)
        return self.session.execute(statement).scalars().first()

    def create_user_answer(self, user_id: int, answer: AnswerResultCreation):
        answer_dict = dict(user_id=user_id, answer_id=answer.answer_id, is_selected=answer.is_selected)
        answer_row = tables.UsersAnswers(**answer_dict)
        self.session.add(answer_row)
        self.session.commit()

    def create_question_result(self, user_id: int, question_id: int, score: float):
        question_dict = dict(user_id=user_id, question_id=question_id, score=score)
        question_row = tables.QuestionsResults(**question_dict)
        self.session.add(question_row)
        self.session.commit()

    def create_test_result(self, user_id: int, max_score: int, score: float, test_id: int):
        test_dict = dict(user_id=user_id, test_id=test_id, max_score=max_score, score=score)
        test_row = tables.Results(**test_dict)
        self.session.add(test_row)
        self.session.commit()

    def get_right_answers(self, answers: List[AnswerResultCreation]):
        right_answers = []
        for ans in answers:
            answer = self.get_answer(ans.answer_id)
            if answer.is_right:
                right_answers.append(ans)
        return right_answers

    def calculate_score(self, user_id: int, course_id: int,
                        questions: List[QuestionResultCreation]) -> float:
        self.check_accessibility(user_id, course_id)
        global_score: float = 0
        for question in questions:
            score: float = 0
            ans_score = len(self.get_right_answers(question.answers)) / len(question.answers)
            for answer_result in question.answers:
                self.create_user_answer(user_id, answer_result)
                answer = self.get_answer(answer_result.answer_id)
                if answer.is_right == answer_result.is_selected:
                    score += ans_score
                else:
                    score -= ans_score
                if score < 0:
                    score = 0
            global_score += score
            self.create_question_result(user_id, question.question_id, score)
        if global_score < 0:
            global_score = 0
        return global_score

    def calculate_result(self, user_id: int, course_id: int,
                         test_id: int,
                         questions: List[QuestionResultCreation]):
        global_score = self.calculate_score(user_id, course_id, questions)
        self.create_test_result(user_id, len(questions), global_score, test_id)

    def calculate_demo_result(self, user_id: int, course_id: int,
                              test_id: int,
                              course_owner_id: int,
                              questions: List[QuestionResultCreation]) -> TestResult:
        self.check_for_moderator_rights(user_id, course_id, course_owner_id)
        global_score = self.calculate_score(user_id, course_id, questions)
        test_result = TestResult(questions=questions,
                                 max_score=len(questions),
                                 score=global_score,
                                 id=test_id,
                                 course_id=course_id,
                                 name="unused",
                                 creation_time="unused")
        return test_result
