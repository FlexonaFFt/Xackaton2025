from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(7), unique=True, index=True)
    rating = Column(Integer, default=5)  
    created_at = Column(DateTime, default=datetime.utcnow)
    queries = relationship("TextQuery", back_populates="user")

class TextQuery(Base):
    __tablename__ = "text_queries"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text)
    processed_text = Column(Text)
    success = Column(Boolean)
    file_id = Column(String, nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(7), ForeignKey("users.user_id"))
    user = relationship("User", back_populates="queries")

class FileStatistics(Base):
    __tablename__ = "file_statistics"

    id = Column(Integer, primary_key=True, index=True)
    file_type = Column(String, index=True)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)