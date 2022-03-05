from pydantic import BaseModel

class BaseCourse(BaseModel):
    name: str
    owner: int

class Course(BaseCourse):
    id: int

    class Config:
        orm_mode = True

class OperationCreate(BaseCourse):
    pass

class OperationUpdate(BaseCourse):
    pass