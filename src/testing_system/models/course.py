from typing import List, Any, Optional

from pydantic import BaseModel
import random


class BaseCourse(BaseModel):
    name: str


class Course(BaseCourse):
    id: int
    owner_id: int
    img: str

    class Config:
        orm_mode = True


class CourseCreate(BaseCourse):
    img: str
    owner_id: int

    def __init__(self, **data: BaseCourse):
        super().__init__(**data)
        self.img = f"img{random.randint(1, 8)}"


class CourseUpdate(BaseCourse):
    img: str
    owner_id: int

class Participants(BaseModel):
    user_id: int
    course_id: int