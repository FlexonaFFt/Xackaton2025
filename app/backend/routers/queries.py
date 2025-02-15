from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_  
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
                    "file_id": query.file_id,  
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

        if user.rating != new_rating:
            old_rating = user.rating
            user.rating = new_rating
            
            if new_rating < 3 and (old_rating >= 3 or old_rating is None):
                notification = models.Notification(
                    user_id=user_id,
                    message="Внимание! Ваш рейтинг упал ниже 3. Постарайтесь улучшить качество запросов."
                )
                db.add(notification)
            
            if new_rating < 2 and (old_rating >= 2 or old_rating is None):
                notification = models.Notification(
                    user_id=user_id,
                    message="Критическое предупреждение! Ваш рейтинг упал ниже 2. Необходимо срочно улучшить качество запросов."
                )
                db.add(notification)
            
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

@router.get("/notifications/{user_id}")
async def get_user_notifications(
    user_id: str,
    db: Session = Depends(database.get_db)
):
    try:
        notifications = db.query(models.Notification).filter(
            and_(
                models.Notification.user_id == user_id,
                models.Notification.is_read == False
            )
        ).all()
        
        return {
            "notifications": [
                {
                    "id": notif.id,
                    "message": notif.message,
                    "created_at": notif.created_at
                }
                for notif in notifications
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving notifications: {str(e)}"
        )

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(database.get_db)
):
    try:
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = True
        db.commit()
        
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error marking notification as read: {str(e)}"
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
@router.get("/statistics/files")
async def get_file_statistics(
    period: str = "all",  # "day", "week", "all"
    db: Session = Depends(database.get_db)
):
    try:
        query = db.query(models.FileStatistics)
        
        if period == "day":
            start_date = datetime.utcnow() - timedelta(days=1)
            query = query.filter(models.FileStatistics.created_at >= start_date)
        elif period == "week":
            start_date = datetime.utcnow() - timedelta(days=7)
            query = query.filter(models.FileStatistics.created_at >= start_date)
        
        stats = query.all()
        
        file_stats = {}
        for stat in stats:
            if stat.file_type not in file_stats:
                file_stats[stat.file_type] = 0
            file_stats[stat.file_type] += stat.count
            
        sorted_stats = sorted(
            file_stats.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            "period": period,
            "statistics": [
                {
                    "file_type": file_type,
                    "count": count
                }
                for file_type, count in sorted_stats
            ],
            "total_files": sum(file_stats.values())
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving file statistics: {str(e)}"
        )