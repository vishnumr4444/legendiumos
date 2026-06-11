"""Legendium OS data model.

Work hierarchy is a single self-referencing table (WorkItem) with a `type`
discriminator: epic > story > task > subtask. This mirrors Jira's model and
keeps dependency / sync logic uniform.
"""
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Text, DateTime, Float,
                        ForeignKey, Boolean)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False)  # admin | lead | employee
    department_id = Column(Integer, ForeignKey("departments.id"))
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(100))
    skills = Column(Text, default="")           # comma separated
    capacity_hours = Column(Float, default=40)  # weekly capacity
    avatar_color = Column(String(7), default="#06b6d4")
    department = relationship("Department", back_populates="members")
    reports = relationship("User", remote_side=[id], backref="subordinates")


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(20), unique=True, nullable=False)
    jira_project_key = Column(String(10))
    members = relationship("User", back_populates="department")
    projects = relationship("Project", back_populates="department")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True)
    description = Column(Text, default="")
    department_id = Column(Integer, ForeignKey("departments.id"))
    status = Column(String(20), default="active")  # active|on_hold|done
    health = Column(String(10), default="green")   # green|amber|red
    target_date = Column(DateTime, nullable=True)
    department = relationship("Department", back_populates="projects")
    work_items = relationship("WorkItem", back_populates="project")


class WorkItem(Base):
    __tablename__ = "work_items"
    id = Column(Integer, primary_key=True)
    type = Column(String(10), nullable=False)  # epic|story|task|subtask
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="todo")   # todo|in_progress|review|blocked|done
    priority = Column(String(10), default="medium")  # low|medium|high|critical
    discipline = Column(String(20), default="development")
    # business|design|development|qa|documentation|deployment|marketing|manufacturing|sales|support
    estimate_hours = Column(Float, default=0)
    logged_hours = Column(Float, default=0)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("work_items.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    jira_key = Column(String(20), nullable=True, index=True)
    project = relationship("Project", back_populates="work_items")
    parent = relationship("WorkItem", remote_side=[id], backref="children")
    assignee = relationship("User", foreign_keys=[assignee_id])
    comments = relationship("Comment", back_populates="work_item",
                            cascade="all, delete-orphan")


class Dependency(Base):
    __tablename__ = "dependencies"
    id = Column(Integer, primary_key=True)
    blocker_id = Column(Integer, ForeignKey("work_items.id"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("work_items.id"), nullable=False)


class Sprint(Base):
    __tablename__ = "sprints"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    state = Column(String(15), default="active")  # future|active|closed


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ai_flags = Column(String(120), default="")  # blocker,risk,dependency,urgent
    work_item = relationship("WorkItem", back_populates="comments")
    author = relationship("User")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String(200), nullable=False)
    kind = Column(String(20), default="other")  # sop|roadmap|notes|vendor|tech|other
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    text_content = Column(Text, default="")  # extracted text used for RAG
    size_bytes = Column(Integer, default=0)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String(300), nullable=False)
    kind = Column(String(20), default="info")  # info|assignment|risk|approval
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(80), nullable=False)
    detail = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
