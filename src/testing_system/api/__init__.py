from fastapi import APIRouter
from .auth import router as auth_router
from .images import router as images_router
from .course import router as course_router
from .course_moderators import router as course_moderators_router
from .test import router as test_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(images_router)
router.include_router(course_router)
router.include_router(course_moderators_router)
router.include_router(test_router)