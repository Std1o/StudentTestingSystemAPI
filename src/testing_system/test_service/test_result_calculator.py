from typing import List
from .test_getter import TestSearchingService
from .. import tables
from ..database import make_query, insert_and_get_id
from ..models.test import Answer
from ..models.test_result import TestResult, QuestionResult, AnswerResult
from ..models.test_result_creation import QuestionResultCreation, AnswerResultCreation


class TestResultCalculatorService(TestSearchingService):

    def get_answer(self, answer_id: int) -> tables.Answers:
        return make_query("SELECT * FROM answers where id=?", tables.Answers, answer_id)

    def get_question(self, question_id: int) -> tables.Questions:
        return make_query("SELECT * FROM questions where id=?", tables.Questions, question_id)

    def create_user_answer(self, user_id: int, answer: AnswerResultCreation):
        query = "INSERT INTO users_answers (user_id, answer_id, is_selected) " \
                "VALUES (?, ?, ?)"
        insert_and_get_id(query, user_id, answer.answer_id, answer.is_selected)

    def create_question_result(self, user_id: int, question_id: int, score: float):
        query = "INSERT INTO questions_results (user_id, question_id, score) " \
                "VALUES (?, ?, ?)"
        insert_and_get_id(query, user_id, question_id, score)

    def create_test_result(self, user_id: int, max_score: int, score: float, test_id: int):
        query = "INSERT INTO results (user_id, test_id, max_score, score) " \
                "VALUES (?, ?, ?, ?)"
        insert_and_get_id(query, user_id, test_id, max_score, score)

    def get_right_answers(self, answers: List[AnswerResultCreation]):
        right_answers = []
        for ans in answers:
            answer = self.get_answer(ans.answer_id)
            if answer.is_right:
                right_answers.append(ans)
        return right_answers

    def calculate_score(self, user_id: int, course_id: int, save: bool,
                        questions: List[QuestionResultCreation]) -> float:
        self.check_accessibility(user_id, course_id)
        global_score: float = 0
        for question in questions:
            score: float = 0
            ans_score = len(self.get_right_answers(question.answers)) / len(question.answers)
            for answer_result in question.answers:
                if save:
                    self.create_user_answer(user_id, answer_result)
                answer = self.get_answer(answer_result.answer_id)
                if answer.is_right == answer_result.is_selected:
                    score += ans_score
                else:
                    score -= ans_score
                if score < 0:
                    score = 0
            global_score += score
            if save:
                self.create_question_result(user_id, question.question_id, score)
        if global_score < 0:
            global_score = 0
        return global_score

    def calculate_result(self, user_id: int, course_id: int,
                         test_id: int,
                         questions: List[QuestionResultCreation]):
        global_score = self.calculate_score(user_id, course_id, True, questions)
        self.create_test_result(user_id, len(questions), global_score, test_id)

    def calculate_demo_result(self, user_id: int, course_id: int,
                              questions_in: List[QuestionResultCreation]) -> TestResult:
        self.check_for_moderator_rights(user_id, course_id)

        global_score: float = 0
        questions: List[QuestionResult] = []
        for question_in in questions_in:
            score: float = 0
            ans_score = len(self.get_right_answers(question_in.answers)) / len(question_in.answers)
            answers: List[AnswerResult] = []
            for answer_in in question_in.answers:
                table_ans = self.get_answer(answer_in.answer_id)
                answer = Answer(
                    answer=table_ans.answer,
                    is_right=table_ans.is_right,
                    id=table_ans.id
                )
                answer_result_dict = answer.dict()
                answer_result_dict['is_selected'] = answer_in.is_selected
                answers.append(AnswerResult(**answer_result_dict))
                if answer.is_right == answer_in.is_selected:
                    score += ans_score
                else:
                    score -= ans_score
                if score < 0:
                    score = 0
            global_score += score
            table_question = self.get_question(question_in.question_id)
            question = QuestionResult(
                question=table_question.question,
                id=table_question.id,
                answers=answers,
                score=score
            )
            questions.append(question)
        if global_score < 0:
            global_score = 0

        test_result = TestResult(questions=questions,
                                 max_score=len(questions),
                                 score=global_score)
        return test_result
