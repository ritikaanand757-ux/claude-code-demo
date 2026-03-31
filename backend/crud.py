"""
CRUD operations for Task model
All database operations should go through this module
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from backend.models import Task
from backend.schemas import TaskCreate, TaskUpdate


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    priority: Optional[str] = None,
    completed: Optional[bool] = None,
    page: Optional[int] = None
) -> List[Task]:
    """
    Get all tasks with optional filtering and pagination

    Args:
        db: Database session
        skip: Number of records to skip (for offset pagination)
        limit: Maximum number of records to return
        priority: Filter by priority (low, medium, high)
        completed: Filter by completion status
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

    # Apply pagination
    if page is not None and page > 0:
        # Page-based pagination (page starts at 1)
        skip = (page - 1) * limit

    tasks = query.offset(skip).limit(limit).all()
    return tasks


def get_task_count(
    db: Session,
    priority: Optional[str] = None,
    completed: Optional[bool] = None
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


def create_task(db: Session, task: TaskCreate) -> Task:
    """
    Create a new task

    Args:
        db: Database session
        task: Task creation data

    Returns:
        Created Task object
    """
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: TaskUpdate) -> Optional[Task]:
    """
    Update an existing task

    Args:
        db: Database session
        task_id: Task ID
        task: Task update data

    Returns:
        Updated Task object or None if not found
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        return None

    update_data = task.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """
    Delete a task

    Args:
        db: Database session
        task_id: Task ID

    Returns:
        True if deleted, False if not found
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        return False

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

    tasks = db.query(Task).filter(
        or_(
            Task.title.ilike(search_pattern),
            Task.description.ilike(search_pattern),
            Task.tags.ilike(search_pattern)
        )
    ).limit(limit).all()

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
    priority_stats = db.query(
        Task.priority,
        func.count(Task.id)
    ).group_by(Task.priority).all()

    priority_counts = {priority: count for priority, count in priority_stats}

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "by_priority": {
            "high": priority_counts.get("high", 0),
            "medium": priority_counts.get("medium", 0),
            "low": priority_counts.get("low", 0)
        }
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
    deleted_count = db.query(Task).filter(Task.id.in_(task_ids)).delete(synchronize_session=False)
    db.commit()
    return deleted_count
