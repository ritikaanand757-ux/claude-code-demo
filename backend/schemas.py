from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    tags: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    tags: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskSearchResponse(TaskResponse):
    """Response model for search results (same as TaskResponse)"""
    pass


class PriorityStats(BaseModel):
    """Statistics by priority"""
    high: int = 0
    medium: int = 0
    low: int = 0


class TaskStatsResponse(BaseModel):
    """Response model for task statistics"""
    total: int
    completed: int
    pending: int
    by_priority: PriorityStats


class BulkDeleteRequest(BaseModel):
    """Request model for bulk delete"""
    task_ids: List[int] = Field(..., min_items=1, description="List of task IDs to delete")


class BulkDeleteResponse(BaseModel):
    """Response model for bulk delete"""
    deleted_count: int
    requested_count: int
