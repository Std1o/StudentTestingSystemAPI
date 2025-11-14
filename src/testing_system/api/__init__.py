from fastapi import APIRouter
from .auth import router as auth_router
from .images import router as images_router
from .course import router as course_router
from .course_moderators import router as course_moderators_router
from .course_management import router as course_management_router
from .test import router as test_router
from .websocket_results import test_router as websocket_results
from .ai import router as ai_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(images_router)
router.include_router(course_router)
router.include_router(course_moderators_router)
router.include_router(course_management_router)
router.include_router(test_router)
router.include_router(websocket_results)
router.include_router(ai_router)