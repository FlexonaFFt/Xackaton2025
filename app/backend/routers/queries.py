from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel  
import database
import models
import random  

router = APIRouter(
    prefix="/queries",
    tags=["queries"]
)

@router.get("/get_user/{user_id}")
async def get_user_queries(
    user_id: str,
    db: Session = Depends(database.get_db)
):
    try:
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        queries = db.query(models.TextQuery).filter(
            models.TextQuery.user_id == user_id
        ).all()

        return {
            "user_id": user_id,
            "queries": [
                {
                    "id": query.id,
                    "original_text": query.original_text,
                    "processed_text": query.processed_text,
                    "success": query.success,
                    "created_at": query.created_at
                }
                for query in queries
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving queries: {str(e)}"
        )

@router.get("/random_users")
async def get_random_users(db: Session = Depends(database.get_db)):
    try:
        users = db.query(models.User).all()
        
        if not users:
            return {
                "random_users": [],
                "total_users": 0,
                "message": "No users found in database"
            }
            
        random_users = random.sample(users, min(5, len(users)))
        return {
            "random_users": [
                {
                    "user_id": user.user_id,
                    "created_at": user.created_at
                }
                for user in random_users
            ],
            "total_users": len(users)
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving random users: {str(e)}"
        )

class UserCreate(BaseModel):
    user_id: str

@router.post("/create_user")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(database.get_db)
):
    try:
        existing_user = db.query(models.User).filter(
            models.User.user_id == user_data.user_id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"User with ID {user_data.user_id} already exists"
            )
        
        new_user = models.User(user_id=user_data.user_id)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "User created successfully",
            "user_id": new_user.user_id,
            "created_at": new_user.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error creating user: {str(e)}"
        )