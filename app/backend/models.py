from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(7), unique=True, index=True)
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