from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel  
import database
import models
import random  
from datetime import datetime, timedelta

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

# Add these new endpoints after existing ones

@router.get("/statistics/time_period")
async def get_time_period_statistics(
    period: str = "day",  # "day", "3days", "week"
    db: Session = Depends(database.get_db)
):
    try:
        now = datetime.utcnow()
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "3days":
            start_date = now - timedelta(days=3)
        elif period == "week":
            start_date = now - timedelta(days=7)
        else:
            raise HTTPException(status_code=400, detail="Invalid period")

        queries = db.query(models.TextQuery).filter(
            models.TextQuery.created_at >= start_date
        ).all()

        success_count = len([q for q in queries if q.success])
        fail_count = len([q for q in queries if not q.success])

        return {
            "period": period,
            "success_count": success_count,
            "fail_count": fail_count,
            "total_count": len(queries)
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving time period statistics: {str(e)}"
        )

@router.get("/statistics/user/{user_id}")
async def get_user_statistics(
    user_id: str,
    db: Session = Depends(database.get_db)
):
    try:
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        queries = db.query(models.TextQuery).filter(
            models.TextQuery.user_id == user_id
        ).all()

        success_count = len([q for q in queries if q.success])
        fail_count = len([q for q in queries if not q.success])
        
        # Calculate and update rating
        total_fails = fail_count
        if total_fails <= 1:
            new_rating = 5
        elif total_fails <= 3:
            new_rating = 4
        elif total_fails <= 4:
            new_rating = 3
        elif total_fails <= 5:
            new_rating = 2
        else:
            new_rating = 1

        # Update user rating if changed
        if user.rating != new_rating:
            user.rating = new_rating
            db.commit()

        return {
            "user_id": user_id,
            "success_count": success_count,
            "fail_count": fail_count,
            "total_count": len(queries),
            "current_rating": new_rating
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving user statistics: {str(e)}"
        )

@router.get("/statistics/rating/{user_id}")
async def get_user_rating(
    user_id: str,
    db: Session = Depends(database.get_db)
):
    try:
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user_id": user_id,
            "rating": user.rating
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving user rating: {str(e)}"
        )