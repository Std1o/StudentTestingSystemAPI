from typing import List, Optional
from fastapi import APIRouter
from ..models.operations import Operation, OperationKind, OperationCreate
from ..database import get_session
from fastapi import Depends
from ..services.operations import OperationService

router = APIRouter(prefix='/operations')

@router.get('/', response_model=List[Operation])
def get_operations(kind: Optional[OperationKind] = None, service: OperationService = Depends()):
    return service.get_list(kind=kind)

@router.get('/{operation_id}', response_model=Operation)
def get_operation(operation_id: int, service: OperationService = Depends()):
    return service.get(operation_id)

@router.post('/', response_model=Operation)
def create_operation(operation_data: OperationCreate, service: OperationService = Depends()):
    return service.create(operation_data)