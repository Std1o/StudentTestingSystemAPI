from typing import List, Optional
from fastapi import APIRouter
from ..models.operations import Operation, OperationKind
from ..database import get_session
from fastapi import Depends
from ..services.operations import OperationService

router = APIRouter(prefix='/operations')

@router.get('/', response_model=List[Operation])
def get_operations(kind: Optional[OperationKind] = None, service: OperationService = Depends()):
    return service.get_list(kind=kind)