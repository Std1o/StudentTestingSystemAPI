import os.path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix='/images')

@router.get('/{image_name}')
def get_image(image_name: str):
    return FileResponse(f"images/{image_name}.png")