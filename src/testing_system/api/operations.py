from typing import List
from fastapi import APIRouter
from ..models.operations import Operation
from ..database import get_session
from fastapi import Depends
from ..services.operations import OperationService

router = APIRouter(prefix='/operations')

@router.get('/', response_model=List[Operation])
def get_operations(service: OperationService = Depends()):
    return service.get_list()