"""
CRUD operations for Task and User models
All database operations should go through this module
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException
from backend.models import Task, User, ActivityLog
from backend.schemas import TaskCreate, TaskUpdate, UserCreate
from backend.auth import get_password_hash

# ============== User CRUD Operations ==============


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email address

    Args:
        db: Database session
        email: User email address

    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username

    Args:
        db: Database session
        username: Username

    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user with hashed password

    Args:
        db: Database session
        user: User creation data

    Returns:
        Created User object
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, username=user.username, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ============== Activity Logging ==============


def log_activity(
    db: Session,
    task_id: int,
    action: str,
    changed_by: int,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
) -> ActivityLog:
    """
    Log an activity event for a task

    Args:
        db: Database session
        task_id: ID of the task being tracked
        action: Type of action (status_change, created, updated, archived)
        changed_by: ID of user who made the change
        old_value: Previous value before change (optional)
        new_value: New value after change (optional)

    Returns:
        Created ActivityLog object
    """
    log_entry = ActivityLog(
        task_id=task_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        changed_by=changed_by,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


# ============== Task CRUD Operations ==============


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    priority: Optional[str] = None,
    completed: Optional[bool] = None,
    status: Optional[str] = None,
    page: Optional[int] = None,
) -> List[Task]:
    """
    Get all tasks with optional filtering and pagination

    Args:
        db: Database session
        skip: Number of records to skip (for offset pagination)
        limit: Maximum number of records to return
        priority: Filter by priority (low, medium, high)
        completed: Filter by completion status
        status: Filter by status (todo, in_progress, done, blocked)
        page: Page number (for page-based pagination, overrides skip)

    Returns:
        List of Task objects
    """
    query = db.query(Task)

    # Apply filters
    if priority:
        query = query.filter(Task.priority == priority)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    if status:
        query = query.filter(Task.status == status)

    # Apply pagination
    if page is not None and page > 0:
        # Page-based pagination (page starts at 1)
        skip = (page - 1) * limit

    tasks = query.offset(skip).limit(limit).all()
    return tasks


def get_task_count(
    db: Session, priority: Optional[str] = None, completed: Optional[bool] = None
) -> int:
    """
    Get total count of tasks with optional filtering

    Args:
        db: Database session
        priority: Filter by priority
        completed: Filter by completion status

    Returns:
        Count of tasks
    """
    query = db.query(Task)

    if priority:
        query = query.filter(Task.priority == priority)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    return query.count()


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """
    Get a specific task by ID

    Args:
        db: Database session
        task_id: Task ID

    Returns:
        Task object or None if not found
    """
    return db.query(Task).filter(Task.id == task_id).first()


def create_task(db: Session, task: TaskCreate, owner_id: int) -> Task:
    """
    Create a new task with owner and activity logging

    Args:
        db: Database session
        task: Task creation data
        owner_id: ID of user creating the task

    Returns:
        Created Task object
    """
    task_data = task.model_dump()
    task_data['owner_id'] = owner_id
    db_task = Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Log task creation
    log_activity(
        db=db,
        task_id=db_task.id,
        action="created",
        changed_by=owner_id,
        new_value=f"Task created with status '{db_task.status}'"
    )

    return db_task


def update_task(
    db: Session, task_id: int, task: TaskUpdate, current_user_id: int
) -> Optional[Task]:
    """
    Update an existing task with business rules and activity logging

    Args:
        db: Database session
        task_id: Task ID
        task: Task update data
        current_user_id: ID of user making the update

    Returns:
        Updated Task object or None if not found

    Raises:
        HTTPException: If business rules are violated
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        return None

    # Business Rule: Only owner can change status
    if task.status and task.status != db_task.status:
        if db_task.owner_id != current_user_id:
            raise HTTPException(
                status_code=403, detail="Only task owner can change status"
            )

        # Log status change
        log_activity(
            db=db,
            task_id=task_id,
            action="status_change",
            changed_by=current_user_id,
            old_value=db_task.status,
            new_value=task.status,
        )

    # Apply updates
    update_data = task.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    # Log general update if not just a status change
    if not task.status or task.status == db_task.status:
        log_activity(
            db=db,
            task_id=task_id,
            action="updated",
            changed_by=current_user_id,
            new_value="Task details updated",
        )

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, current_user_id: int) -> bool:
    """
    Delete a task with business rule validation

    Args:
        db: Database session
        task_id: Task ID
        current_user_id: ID of user attempting deletion

    Returns:
        True if deleted, False if not found

    Raises:
        HTTPException: If business rules are violated
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        return False

    # Business Rule: Cannot delete in-progress tasks
    if db_task.status == "in_progress":
        raise HTTPException(
            status_code=400, detail="Cannot delete tasks that are in progress"
        )

    # Business Rule: Only owner can delete
    if db_task.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Only task owner can delete")

    db.delete(db_task)
    db.commit()
    return True


def search_tasks(db: Session, query: str, limit: int = 50) -> List[Task]:
    """
    Search tasks by keyword in title, description, or tags

    Args:
        db: Database session
        query: Search keyword
        limit: Maximum number of results

    Returns:
        List of matching Task objects
    """
    search_pattern = f"%{query}%"

    tasks = (
        db.query(Task)
        .filter(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern),
                Task.tags.ilike(search_pattern),
            )
        )
        .limit(limit)
        .all()
    )

    return tasks


def get_task_statistics(db: Session) -> dict:
    """
    Get task statistics (total, by status, by priority)

    Args:
        db: Database session

    Returns:
        Dictionary with task statistics
    """
    total = db.query(Task).count()
    completed = db.query(Task).filter(Task.completed == True).count()
    pending = db.query(Task).filter(Task.completed == False).count()

    # Count by priority
    priority_stats = (
        db.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )

    priority_counts = {priority: count for priority, count in priority_stats}

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "by_priority": {
            "high": priority_counts.get("high", 0),
            "medium": priority_counts.get("medium", 0),
            "low": priority_counts.get("low", 0),
        },
    }


def bulk_delete_tasks(db: Session, task_ids: List[int]) -> int:
    """
    Delete multiple tasks by their IDs

    Args:
        db: Database session
        task_ids: List of task IDs to delete

    Returns:
        Number of tasks deleted
    """
    deleted_count = (
        db.query(Task).filter(Task.id.in_(task_ids)).delete(synchronize_session=False)
    )
    db.commit()
    return deleted_count


def get_task_history(db: Session, task_id: int) -> Optional[dict]:
    """
    Get activity history for a specific task

    Generates a simple activity log showing:
    - When the task was created
    - When the task was last updated (if different from created)

    Args:
        db: Database session
        task_id: Task ID

    Returns:
        Dictionary with task_id, task_title, and events list, or None if task not found

    Note:
        This is a simplified history based on created_at and updated_at timestamps.
        For detailed status change tracking, implement an audit log table.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return None

    events = []

    # Add created event
    events.append(
        {
            "event_type": "created",
            "timestamp": task.created_at,
            "description": f"Task '{task.title}' was created",
            "details": {
                "initial_status": task.status if task.status else "todo",
                "initial_priority": task.priority if task.priority else "medium",
                "completed": task.completed,
            },
        }
    )

    # Add updated event if task was modified
    if task.updated_at and task.created_at and task.updated_at != task.created_at:
        events.append(
            {
                "event_type": "updated",
                "timestamp": task.updated_at,
                "description": f"Task '{task.title}' was last updated",
                "details": {
                    "current_status": task.status,
                    "current_priority": task.priority,
                    "completed": task.completed,
                },
            }
        )

    return {"task_id": task.id, "task_title": task.title, "events": events}


# ============== Business Rules Functions ==============


def get_overdue_tasks(db: Session, current_time: datetime) -> List[Task]:
    """
    Get all tasks past their due date that aren't completed

    Args:
        db: Database session
        current_time: Current datetime for comparison

    Returns:
        List of overdue Task objects
    """
    return (
        db.query(Task)
        .filter(
            Task.due_date < current_time,
            Task.status != "done",
            Task.is_archived == False,
        )
        .all()
    )


def get_archived_tasks(db: Session, owner_id: Optional[int] = None) -> List[Task]:
    """
    Get all archived tasks, optionally filtered by owner

    Args:
        db: Database session
        owner_id: Optional user ID to filter by owner

    Returns:
        List of archived Task objects
    """
    query = db.query(Task).filter(Task.is_archived == True)
    if owner_id:
        query = query.filter(Task.owner_id == owner_id)
    return query.all()


def archive_task(
    db: Session, task_id: int, current_user_id: int, reason: Optional[str] = None
) -> Optional[Task]:
    """
    Archive a task

    Args:
        db: Database session
        task_id: Task ID to archive
        current_user_id: ID of user archiving the task
        reason: Optional reason for archiving

    Returns:
        Archived Task object or None if not found
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None

    db_task.is_archived = True
    db_task.archived_at = datetime.utcnow()

    log_activity(
        db=db,
        task_id=task_id,
        action="archived",
        changed_by=current_user_id,
        new_value=reason or "Manual archive",
    )

    db.commit()
    db.refresh(db_task)
    return db_task


def flag_overdue_tasks(db: Session) -> int:
    """
    Flag tasks past their due date as overdue (background job)

    Args:
        db: Database session

    Returns:
        Number of tasks flagged as overdue
    """
    current_time = datetime.utcnow()
    count = (
        db.query(Task)
        .filter(
            Task.due_date < current_time,
            Task.status != "done",
            Task.is_overdue == False,
        )
        .update({Task.is_overdue: True})
    )
    db.commit()
    return count


def auto_archive_old_tasks(db: Session, days: int = 90) -> int:
    """
    Auto-archive tasks older than X days in todo status

    Args:
        db: Database session
        days: Number of days threshold (default: 90)

    Returns:
        Number of tasks auto-archived
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    count = (
        db.query(Task)
        .filter(
            Task.created_at < cutoff_date,
            Task.status == "todo",
            Task.is_archived == False,
        )
        .update({Task.is_archived: True, Task.archived_at: datetime.utcnow()})
    )
    db.commit()
    return count


def get_activity_logs(db: Session, task_id: int) -> List[ActivityLog]:
    """
    Get all activity logs for a task

    Args:
        db: Database session
        task_id: Task ID

    Returns:
        List of ActivityLog objects ordered by timestamp (most recent first)
    """
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.task_id == task_id)
        .order_by(ActivityLog.changed_at.desc())
        .all()
    )
