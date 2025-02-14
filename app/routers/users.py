from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

class User(BaseModel):
    id: int
    name: str
    email: str

@router.get("/")
async def get_users():
    return {"message": "List of users"}

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "message": "User details"}