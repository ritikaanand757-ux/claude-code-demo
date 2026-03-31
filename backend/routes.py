"""
API Routes for Task Management
All route handlers - business logic delegated to CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend import crud
from backend.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskSearchResponse, TaskStatsResponse, BulkDeleteRequest, BulkDeleteResponse


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/search", response_model=List[TaskSearchResponse])
def search_tasks(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
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
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$", description="Filter by priority"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: Session = Depends(get_db)
):
    """
    Get all tasks with optional filtering and pagination

    - **skip**: Number of records to skip (for offset pagination)
    - **limit**: Maximum number of records (default: 20, max: 100)
    - **page**: Page number (overrides skip, starts at 1)
    - **priority**: Filter by priority (low, medium, high)
    - **completed**: Filter by completion status (true/false)
    """
    tasks = crud.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        page=page,
        priority=priority,
        completed=completed
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
            detail=f"Task with id {task_id} not found"
        )

    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task

    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **priority**: Task priority - low, medium, or high (default: medium)
    - **tags**: Comma-separated tags (optional)
    - **due_date**: Due date (optional)
    - **completed**: Completion status (default: false)
    """
    return crud.create_task(db=db, task=task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update an existing task

    - **task_id**: Task ID
    - All fields are optional - only provided fields will be updated
    """
    db_task = crud.update_task(db=db, task_id=task_id, task=task)

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task

    - **task_id**: Task ID
    """
    success = crud.delete_task(db=db, task_id=task_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
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
            detail="task_ids list cannot be empty"
        )

    deleted_count = crud.bulk_delete_tasks(db=db, task_ids=request.task_ids)

    return {
        "deleted_count": deleted_count,
        "requested_count": len(request.task_ids)
    }
