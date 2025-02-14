from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(7), unique=True, index=True)
    rating = Column(Integer, default=5)  # Add this line
    created_at = Column(DateTime, default=datetime.utcnow)
    queries = relationship("TextQuery", back_populates="user")

class TextQuery(Base):
    __tablename__ = "text_queries"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text)
    processed_text = Column(Text)
    success = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(7), ForeignKey("users.user_id"))
    user = relationship("User", back_populates="queries")