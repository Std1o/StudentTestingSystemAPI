from typing import List, Optional
from pydantic import BaseModel
import random
from .auth import User


class BaseCourse(BaseModel):
    name: str


class Course(BaseCourse):
    id: int
    owner_id: int
    img: str
    course_code: str
    participants: List[User]
    moderators: Optional[List[User]]

    class Config:
        orm_mode = True


class CourseCreate(BaseCourse):
    img: str
    owner_id: int
    course_code: str

    def __init__(self, **data: BaseCourse):
        super().__init__(**data)
        self.img = f"img{random.randint(1, 8)}"


class CourseUpdate(BaseCourse):
    pass


class Participants(BaseModel):
    user_id: int
    course_id: int


class Moderator(BaseModel):
    user_id: int
    course_id: int
