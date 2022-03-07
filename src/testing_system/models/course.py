from typing import List, Any, Optional

from pydantic import BaseModel
import random

from .auth import User
from .. import tables


class BaseCourse(BaseModel):
    name: str


class Course(BaseCourse):
    id: int
    owner_id: int
    img: str
    course_code: str
    participants: List[User]

    class Config:
        orm_mode = True


def generate_course_code() -> str:
    seq = "abcdefghijklmnopqrstuvwxyz0123456789"
    code = ''
    for i in range(0, 6):
        code += seq[random.randint(0, len(seq))]
    return code.upper()


class CourseCreate(BaseCourse):
    img: str
    owner_id: int
    course_code: str

    def __init__(self, **data: BaseCourse):
        super().__init__(**data)
        self.img = f"img{random.randint(1, 8)}"
        self.course_code = generate_course_code()


class CourseUpdate(BaseCourse):
    img: str
    owner_id: int
    course_code: str


class Participants(BaseModel):
    user_id: int
    course_id: int
