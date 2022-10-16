from typing import List, Optional
from pydantic import BaseModel
import random
from .auth import User, BaseUser


class BaseCourse(BaseModel):
    name: str


class CourseUsers(BaseUser):
    user_id: int
    is_moderator: bool
    is_owner: bool


class Course(BaseCourse):
    id: int
    img: str
    course_code: str
    participants: List[CourseUsers]

    class Config:
        orm_mode = True


class CourseCreate(BaseCourse):
    img: str
    course_code: str

    def __init__(self, **data: BaseCourse):
        super().__init__(**data)
        self.img = f"img{random.randint(1, 8)}"


class CourseUpdate(BaseCourse):
    pass


class Participants(BaseModel):
    user_id: int
    course_id: int
    is_moderator: bool = False
    is_owner: bool = False
