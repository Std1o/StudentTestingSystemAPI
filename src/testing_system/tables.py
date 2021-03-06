import datetime

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.Text, unique=True)
    username = sa.Column(sa.Text)
    password_hash = sa.Column(sa.Text)


class Course(Base):
    __tablename__ = 'courses'

    id = sa.Column(sa.Integer, primary_key=True)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    name = sa.Column(sa.String)
    course_code = sa.Column(sa.String, unique=True)
    img = sa.Column(sa.String)


class Participants(Base):
    __tablename__ = 'participants'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    course_id = sa.Column(sa.Integer, sa.ForeignKey(Course.owner_id))


class Answers(Base):
    __tablename__ = 'answers'

    id = sa.Column(sa.Integer, primary_key=True)
    question_id = sa.Column(sa.Integer)
    answer = sa.Column(sa.String)
    is_right = sa.Column(sa.Boolean)


class Questions(Base):
    __tablename__ = 'questions'

    id = sa.Column(sa.Integer, primary_key=True)
    test_id = sa.Column(sa.Integer)
    question = sa.Column(sa.String)


class Test(Base):
    __tablename__ = 'tests'

    id = sa.Column(sa.Integer, primary_key=True)
    course_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String)
    creation_time = sa.Column(sa.Date)


class UsersAnswers(Base):
    __tablename__ = 'users_answers'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    answer_id = sa.Column(sa.Integer, sa.ForeignKey(Answers.id))
    is_selected = sa.Column(sa.Boolean)

class QuestionsResults(Base):
    __tablename__ = 'questions_results'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    question_id = sa.Column(sa.Integer, sa.ForeignKey(Questions.id))
    score = sa.Column(sa.Float)


class Results(Base):
    __tablename__ = 'results'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    test_id = sa.Column(sa.Integer, sa.ForeignKey(Test.id))
    max_score = sa.Column(sa.Integer)
    score = sa.Column(sa.Float)


class Moderators(Base):
    __tablename__ = 'moderators'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    course_id = sa.Column(sa.Integer, sa.ForeignKey(Course.owner_id))