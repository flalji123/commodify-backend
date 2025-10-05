from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# ---------- Existing ----------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Keep companies for CRM
class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    country = Column(String, index=True, default="")
    notes = Column(Text, default="")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------- New: Projects ----------
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    client = Column(String, default="")
    status = Column(String, index=True, default="Planning")  # Planning|In Progress|On Hold|Completed
    priority = Column(String, default="Medium")              # Low|Medium|High|Critical
    start_date = Column(String, default="")                  # ISO date string
    end_date = Column(String, default="")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------- New: Tasks (with subtasks & project link) ----------
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # subtask
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(String, index=True, default="todo")      # todo|doing|done
    progress = Column(Integer, default=0)                    # 0..100
    priority = Column(String, default="Normal")              # Low|Normal|High|Critical
    due_date = Column(String, default="")                    # ISO date string
    assignee = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------- New: Comments ----------
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------- New: Team membership ----------
class TeamMembership(Base):
    __tablename__ = "team_memberships"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="Member")  # Admin|Manager|Member|Viewer
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------- New: Uploaded files (metadata only) ----------
class FileAsset(Base):
    __tablename__ = "file_assets"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    size = Column(Integer, default=0)
    path = Column(String, default="")  # storage path (e.g., /tmp/uploads/xyz) – ephemeral on free Render
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------- New: Activity log ----------
class Activity(Base):
    __tablename__ = "activity"
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verb = Column(String, nullable=False)        # e.g., "created task", "updated project"
    object_type = Column(String, nullable=False) # "project" | "task" | "comment" | "file"
    object_id = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
