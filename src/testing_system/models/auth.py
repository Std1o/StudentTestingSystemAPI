from pydantic import BaseModel

class BaseUser(BaseModel):
    email: str
    username: str

class UserCreate(BaseUser):
    password: str

class User(BaseUser):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class PrivateUser(BaseUser):
    id: int
    access_token: str
    token_type: str = 'bearer'

    class Config:
        orm_mode = True