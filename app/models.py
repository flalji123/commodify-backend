
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from .database import Base
class User(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True); email=Column(String, unique=True); password_hash=Column(String)
    created_at=Column(DateTime, default=datetime.utcnow)
class Company(Base):
    __tablename__="companies"
    id=Column(Integer, primary_key=True); name=Column(String); country=Column(String, default=""); notes=Column(Text, default="")
    created_by=Column(Integer, ForeignKey("users.id")); created_at=Column(DateTime, default=datetime.utcnow)
class Task(Base):
    __tablename__="tasks"
    id=Column(Integer, primary_key=True); title=Column(String); status=Column(String, default="todo")
    created_by=Column(Integer, ForeignKey("users.id")); created_at=Column(DateTime, default=datetime.utcnow)
