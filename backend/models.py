"""
Database models for Task Manager application.

This module defines SQLAlchemy ORM models for the application.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class User(Base):
    """
    User model representing a user in the task management system.

    This model stores user authentication and profile information.

    Attributes:
        id (int): Unique identifier for the user (primary key)
        username (str): Unique username (required, indexed)
        email (str): Unique email address (required, indexed)
        hashed_password (str): Hashed password (required)
        is_active (bool): Whether the user account is active (default: True)
        created_at (datetime): Timestamp when user was created (auto-generated)
        updated_at (datetime): Timestamp when user was last updated (auto-updated)
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Task(Base):
    """
    Task model representing a task in the task management system.

    This model stores task information including title, description, completion status,
    priority level, tags, due date, ownership, and lifecycle management fields.

    Attributes:
        id (int): Unique identifier for the task (primary key)
        title (str): Task title (required, 5-100 characters)
        description (str): Detailed task description (optional)
        completed (bool): Task completion status (default: False)
        priority (str): Priority level - 'low', 'medium', or 'high' (default: 'medium')
        status (str): Task status - 'todo', 'in_progress', 'done', or 'blocked' (default: 'todo')
        tags (str): Comma-separated list of tags (optional)
        due_date (datetime): Task due date with timezone (optional)
        owner_id (int): Foreign key to user who owns this task (required)
        completion_note (str): Note explaining what was completed (required when status='done')
        is_archived (bool): Whether task is archived (default: False)
        is_overdue (bool): Whether task is past due date and not completed (default: False)
        archived_at (datetime): Timestamp when task was archived (optional)
        created_at (datetime): Timestamp when task was created (auto-generated)
        updated_at (datetime): Timestamp when task was last updated (auto-updated)
    """

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "LENGTH(title) >= 5 AND LENGTH(title) <= 100", name="check_title_length"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="medium")  # low, medium, high
    status = Column(String, default="todo")  # todo, in_progress, done, blocked
    tags = Column(String, nullable=True)  # Comma-separated tags
    due_date = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    completion_note = Column(String, nullable=True)
    is_archived = Column(Boolean, default=False)
    is_overdue = Column(Boolean, default=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", backref="tasks")

    def to_dict(self):
        """
        Convert the Task object to a dictionary representation.

        Returns:
            dict: Dictionary containing all task fields with properly formatted
                  datetime values in ISO 8601 format.

        Example:
            {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "medium",
                "status": "todo",
                "tags": "shopping,personal",
                "due_date": "2024-01-20T18:00:00Z",
                "owner_id": 1,
                "completion_note": None,
                "is_archived": False,
                "is_overdue": False,
                "archived_at": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "status": self.status,
            "tags": self.tags,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "owner_id": self.owner_id,
            "completion_note": self.completion_note,
            "is_archived": self.is_archived,
            "is_overdue": self.is_overdue,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ActivityLog(Base):
    """
    ActivityLog model for tracking task lifecycle changes.

    This model provides an audit trail of all significant changes to tasks,
    including status changes, creation, updates, and archiving. Essential for
    tracking accountability and understanding task history in a team environment.

    Attributes:
        id (int): Unique identifier for the log entry (primary key)
        task_id (int): Foreign key to the task being tracked (required)
        action (str): Type of action - 'status_change', 'created', 'updated', 'archived' (required)
        old_value (str): Previous value before the change (optional)
        new_value (str): New value after the change (optional)
        changed_by (int): Foreign key to user who made the change (required)
        changed_at (datetime): Timestamp when change occurred (auto-generated)
    """

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    action = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", backref="activity_logs")
    user = relationship("User")
