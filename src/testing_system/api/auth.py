from fastapi import APIRouter, Depends
from ..models.auth import UserCreate, Token, User, PrivateUser
from fastapi.security import OAuth2PasswordRequestForm

from ..services.auth import AuthService, get_current_user

router = APIRouter(prefix='/auth')


@router.post('/sign-up', response_model=PrivateUser)
def sign_up(user_data: UserCreate, service: AuthService = Depends()):
    return service.reg(user_data)


@router.post('/sign-in', response_model=PrivateUser)
def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends()):
    return service.auth(form_data.username, form_data.password)


@router.get('/user', response_model=User)
def get_user(user: User = Depends(get_current_user)):
    return user
