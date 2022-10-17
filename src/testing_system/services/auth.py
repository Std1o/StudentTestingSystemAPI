from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_session, make_query
from ..models.auth import User, UserCreate, PrivateUser
from ..models.tables import User
from ..settings import settings
from jose import jwt, JWTError
from ..models import tables

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign-in')


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return AuthService.validate_token(token)


class AuthService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def validate_token(cls, token: str) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )
        try:
            payload = jwt.decode(token, settings.jwt_sercret, algorithms=[settings.jwt_algorithm])
        except JWTError:
            raise exception from None

        user_data = payload.get('user')

        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise exception from None
        return user

    @classmethod
    def create_token(cls, user: tables.User) -> str:
        user_data = User.from_orm(user)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=settings.jwt_expiration),
            'sub': str(user_data.id),
            'user': user_data.dict()
        }
        token = jwt.encode(payload, settings.jwt_sercret, algorithm=settings.jwt_algorithm)
        return token

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_user_by_email(self, email: str) -> Optional[User]:
        user = make_query("SELECT * FROM users where email=? LIMIT 1", email)
        if not user:
            return None
        return tables.User(**user)

    def reg(self, user_data: UserCreate) -> PrivateUser:
        if self.get_user_by_email(user_data.email):
            raise HTTPException(status_code=418, detail="User with this email already exists")
        password_hash = self.hash_password(user_data.password)
        query = "INSERT INTO users (email, username, password_hash) " \
                "VALUES ("+f'"{user_data.email}"'+","\
                + f'"{user_data.username}"'+"," + f'"{password_hash}"'
        query += ");"
        make_query(query)
        created_user = self.get_user_by_email(user_data.email)
        token = self.create_token(created_user)
        return PrivateUser(email=created_user.email,
                           username=created_user.username,
                           id=created_user.id,
                           access_token=token)

    def auth(self, email: str, password: str) -> PrivateUser:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )
        user = self.get_user_by_email(email)
        if not user:
            raise exception
        if not self.verify_password(password, user.password_hash):
            raise exception
        token = self.create_token(user)
        return PrivateUser(email=user.email,
                           username=user.username,
                           id=user.id,
                           access_token=token)
