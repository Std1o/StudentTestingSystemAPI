from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_session
from .. import tables
from ..models.test import BaseTest, Test, BaseQuestion, Question, BaseAnswer, Answer
import datetime
from .. import constants
from sqlalchemy import select

from ..models.test_result_creation import QuestionResultCreation, AnswerResultCreation, TestResultCreation


class TestService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    # support functions
    def check_accessibility(self, user_id: int, course_id: int):
        if course_id not in self.get_course_ids(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)

    def get_course_ids(self, user_id: int) -> List[int]:
        statement = select(tables.Participants.course_id).filter_by(user_id=user_id)
        return self.session.execute(statement).scalars().all()

    def create_test(self, test_data: BaseTest):
        test = tables.Test(**dict(course_id=test_data.course_id,
                                  name=test_data.name,
                                  creation_time=datetime.datetime.now()))
        self.session.add(test)
        self.session.commit()
        return test

    def get_tests_by_course_id(self, course_id: int) -> List[tables.Test]:
        query = self.session.query(tables.Test)
        query = query.filter_by(course_id=course_id)
        tests = query.all()
        return tests

    def get_questions(self, test_id: int) -> List[tables.Questions]:
        statement = select(tables.Questions).filter_by(test_id=test_id)
        return self.session.execute(statement).scalars().all()

    def get_answers(self, question_id: int) -> List[tables.Answers]:
        statement = select(tables.Answers).filter_by(question_id=question_id)
        return self.session.execute(statement).scalars().all()

    def get_answer(self, answer_id: int) -> tables.Answers:
        statement = select(tables.Answers).filter_by(id=answer_id)
        return self.session.execute(statement).scalars().first()

    def get_last_test_id(self, test_data: BaseTest):
        tests = self.get_tests_by_course_id(test_data.course_id)
        return tests[-1].id

    def create_question(self, test_id: int, question: BaseQuestion):
        question_row = tables.Questions(**dict(test_id=test_id, question=question.question))
        self.session.add(question_row)
        self.session.commit()

    def get_last_question_id(self, test_id: int):
        query = self.session.query(tables.Questions)
        query = query.filter_by(test_id=test_id)
        questions = query.all()
        return questions[-1].id

    def create_answer(self, test_id: int, answer: BaseAnswer):
        answer_dict = answer.dict()
        answer_dict['question_id'] = self.get_last_question_id(test_id)
        answer_row = tables.Answers(**answer_dict)
        self.session.add(answer_row)
        self.session.commit()

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

    # main functions
    def create(self, user_id: int, course_owner_id: int, test_data: BaseTest) -> Test:
        if course_owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.ACCESS_ERROR)
        self.create_test(test_data)
        test_id = self.get_last_test_id(test_data)
        for question in test_data.questions:
            self.create_question(test_id, question)
            for answer in question.answers:
                self.create_answer(test_id, answer)
        test = self._get(user_id, test_data.course_id, test_id)
        return test

    def get_tests(self, user_id: int, course_id: int, ) -> List[Test]:
        self.check_accessibility(user_id, course_id)
        tests = []
        for test in self.get_tests_by_course_id(course_id):
            test: Test = test
            test.questions = []
            for question_row in self.get_questions(test.id):
                answers: List[Answer] = []
                for ans in self.get_answers(question_row.id):
                    answers.append(Answer(id=ans.id, answer=ans.answer, is_right=None))
                question = Question(id=question_row.id,
                                    question=question_row.question,
                                    answers=answers)
                test.questions.append(question)
            tests.append(test)
        return tests

    def _get(self, user_id: int, course_id: int, test_id: int) -> Test:
        tests = self.get_tests(user_id, course_id)
        tests = [test for test in tests if test.course_id == course_id and test.id == test_id]
        if not tests:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return tests[0]

    def get(self, user_id: int, course_id: int, test_id: int) -> Test:
        return self._get(user_id, course_id, test_id)

    def calculate_result(self, user_id: int, course_id: int,
                         test_id: int,
                         questions: List[QuestionResultCreation],
                         answers: List[AnswerResultCreation]):
        self.check_accessibility(user_id, course_id)
        right_answers = []
        for ans in answers:
            answer = self.get_answer(ans.answer_id)
            if answer.is_right:
                right_answers.append(ans)
        score: float = 0
        for answer_result in answers:
            self.create_user_answer(user_id, answer_result)
            answer = self.get_answer(answer_result.answer_id)

            ans_score = 1.0 / len(right_answers)
            if answer.is_right == answer_result.is_selected:
                score += ans_score
            else:
                score -= ans_score
            if score < 0:
                score = 0
        for question in questions:
            self.create_question_result(user_id, question.question_id, score)
        self.create_test_result(user_id, len(questions), score, test_id)
