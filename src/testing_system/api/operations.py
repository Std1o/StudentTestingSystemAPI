from typing import List
from fastapi import APIRouter
from sqlalchemy.orm import Session

from ..models.operations import Operation
from ..database import get_session
from .. import tables
from fastapi import Depends

router = APIRouter(prefix='/operations')

@router.get('/', response_model=List[Operation])
def get_operations(session: Session = Depends(get_session)):
    operations = (session.query(tables.Operations).all())
    return operations