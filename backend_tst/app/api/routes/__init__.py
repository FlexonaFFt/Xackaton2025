from fastapi import APIRouter
from .requests import router as requests_router
from .classification import router as classification_router

api_router = APIRouter()

api_router.include_router(requests_router, prefix="/requests", tags=["requests"])
api_router.include_router(classification_router, prefix="/classification", tags=["classification"])