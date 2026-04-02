"""
API Routes for Task Management.

This module defines all HTTP route handlers for the Task Manager API.
All business logic is delegated to CRUD operations in the crud module.

The routes follow RESTful conventions and include:
- CRUD operations for tasks (GET, POST, PUT, DELETE)
- Search functionality
- Statistics endpoint
- Bulk operations

All routes are prefixed with /api/tasks and include comprehensive
request validation, error handling, and response models.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend import crud
from backend.auth import get_current_user
from backend.models import User
from backend.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskSearchResponse,
    TaskStatsResponse,
    BulkDeleteRequest,
    BulkDeleteResponse,
    TaskHistoryResponse,
    ActivityLogResponse,
    ArchiveRequest,
)

# Initialize the APIRouter for all task-related endpoints
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/search", response_model=List[TaskSearchResponse])
def search_tasks(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    """
    Search tasks by keyword in title, description, or tags

    - **q**: Search query (required)
    - **limit**: Maximum number of results (default: 50, max: 100)
    """
    tasks = crud.search_tasks(db=db, query=q, limit=limit)
    return tasks


@router.get("/stats", response_model=TaskStatsResponse)
def get_task_statistics(db: Session = Depends(get_db)):
    """
    Get task statistics including:
    - Total task count
    - Completed vs pending tasks
    - Tasks by priority (high, medium, low)
    """
    stats = crud.get_task_statistics(db=db)
    return stats


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    page: Optional[int] = Query(None, ge=1, description="Page number (overrides skip)"),
    priority: Optional[str] = Query(
        None, regex="^(low|medium|high)$", description="Filter by priority"
    ),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    status: Optional[str] = Query(
        None, regex="^(todo|in_progress|done|blocked)$", description="Filter by status"
    ),
    db: Session = Depends(get_db),
):
    """
    Get all tasks with optional filtering and pagination

    - **skip**: Number of records to skip (for offset pagination)
    - **limit**: Maximum number of records (default: 20, max: 100)
    - **page**: Page number (overrides skip, starts at 1)
    - **priority**: Filter by priority (low, medium, high)
    - **completed**: Filter by completion status (true/false)
    - **status**: Filter by status (todo, in_progress, done, blocked)
    """
    tasks = crud.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        page=page,
        priority=priority,
        completed=completed,
        status=status,
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a specific task by ID

    - **task_id**: Task ID
    """
    task = crud.get_task_by_id(db=db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return task


@router.get("/{task_id}/history", response_model=TaskHistoryResponse)
def get_task_history(task_id: int, db: Session = Depends(get_db)):
    """
    Get activity history for a specific task

    Returns a simple activity log showing:
    - When the task was created
    - When the task was last updated

    - **task_id**: Task ID

    Note: This is a simplified history based on timestamps.
    For detailed status change tracking, implement an audit log system.
    """
    history = crud.get_task_history(db=db, task_id=task_id)

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return history


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task owned by the current user

    - **title**: Task title (required, 5-100 characters)
    - **description**: Task description (optional)
    - **priority**: Task priority - low, medium, or high (default: medium)
    - **tags**: Comma-separated tags (optional)
    - **due_date**: Due date (optional, required for high priority tasks)
    - **completed**: Completion status (default: false)
    - **status**: Task status (default: todo)
    """
    return crud.create_task(db=db, task=task, owner_id=current_user.id)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing task (requires authentication)

    - **task_id**: Task ID
    - All fields are optional - only provided fields will be updated
    - Only task owner can update task (unless admin)
    - Only task owner can change status (unless admin)
    - Completion note required when marking task as done
    """
    db_task = crud.update_task(
        db=db,
        task_id=task_id,
        task=task,
        current_user_id=current_user.id,
        is_admin=current_user.is_admin,
    )

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a task (requires authentication)

    - **task_id**: Task ID
    - Only task owner can delete (unless admin)
    - Cannot delete in-progress tasks (unless admin)
    - Admins can delete any task
    """
    success = crud.delete_task(
        db=db,
        task_id=task_id,
        current_user_id=current_user.id,
        is_admin=current_user.is_admin,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return None


@router.post("/bulk/delete", response_model=BulkDeleteResponse)
def bulk_delete_tasks(request: BulkDeleteRequest, db: Session = Depends(get_db)):
    """
    Delete multiple tasks at once

    - **task_ids**: List of task IDs to delete
    """
    if not request.task_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="task_ids list cannot be empty",
        )

    deleted_count = crud.bulk_delete_tasks(db=db, task_ids=request.task_ids)

    return {"deleted_count": deleted_count, "requested_count": len(request.task_ids)}


# ============== Business Rules Endpoints ==============


@router.get("/overdue", response_model=List[TaskResponse])
def get_overdue_tasks(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get all overdue tasks (past due date, not completed)

    Returns tasks that:
    - Have a due date in the past
    - Are not in 'done' status
    - Are not archived
    """
    current_time = datetime.utcnow()
    tasks = crud.get_overdue_tasks(db=db, current_time=current_time)
    return tasks


@router.get("/archived", response_model=List[TaskResponse])
def get_archived_tasks(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get all archived tasks for current user

    Returns tasks owned by the current user that have been archived.
    """
    return crud.get_archived_tasks(db=db, owner_id=current_user.id)


@router.post("/{task_id}/archive", response_model=TaskResponse)
def archive_task(
    task_id: int,
    archive_req: ArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually archive a task

    - **task_id**: Task ID to archive
    - **reason**: Optional reason for archiving
    """
    task = crud.archive_task(
        db=db,
        task_id=task_id,
        current_user_id=current_user.id,
        reason=archive_req.reason,
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.get("/{task_id}/activity", response_model=List[ActivityLogResponse])
def get_task_activity(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get activity log for a task

    Returns all activity events for the specified task, including:
    - Task creation
    - Status changes
    - Updates
    - Archiving

    Events are ordered by timestamp (most recent first).
    """
    # Verify task exists
    task = crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    logs = crud.get_activity_logs(db=db, task_id=task_id)
    return logs


@router.post("/maintenance/run", tags=["admin"])
def run_maintenance(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Run task maintenance job (authenticated users only)

    Performs automated maintenance:
    - Flags overdue tasks (past due date, not completed)
    - Auto-archives tasks older than 90 days in 'todo' status

    Returns:
        dict: Statistics about maintenance operations
            - overdue_flagged: Number of tasks flagged as overdue
            - auto_archived: Number of tasks auto-archived
    """
    from backend.background_jobs import run_task_maintenance

    result = run_task_maintenance()
    return result
