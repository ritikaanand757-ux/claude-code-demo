from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional, List, Dict
from datetime import datetime

# ============== User Schemas ==============


class UserBase(BaseModel):
    """Base user schema with common attributes"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for user registration"""

    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response (excludes password)"""

    id: int
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload data"""

    email: Optional[str] = None


# ============== Task Schemas ==============


class TaskBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    status: str = Field(default="todo", pattern="^(todo|in_progress|done|blocked)$")
    tags: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    @model_validator(mode='after')
    def high_priority_needs_due_date(self):
        if self.priority == 'high' and self.due_date is None:
            raise ValueError('High priority tasks must have a due date')
        return self


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    status: Optional[str] = Field(
        default=None, pattern="^(todo|in_progress|done|blocked)$"
    )
    tags: Optional[str] = None
    due_date: Optional[datetime] = None
    completion_note: Optional[str] = None

    @model_validator(mode='after')
    def validate_business_rules(self):
        # Completion note required when marking as done
        if self.status == 'done' and not self.completion_note:
            raise ValueError('Completion note required when marking task as done')

        # High priority tasks must have due date
        if self.priority == 'high' and self.due_date is None:
            raise ValueError('High priority tasks must have a due date')

        return self


class TaskResponse(TaskBase):
    id: int
    owner_id: int
    completion_note: Optional[str] = None
    is_archived: bool = False
    is_overdue: bool = False
    archived_at: Optional[datetime] = None
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

    task_ids: List[int] = Field(
        ..., min_items=1, description="List of task IDs to delete"
    )


class BulkDeleteResponse(BaseModel):
    """Response model for bulk delete"""

    deleted_count: int
    requested_count: int


class ActivityEvent(BaseModel):
    """Single activity event in task history"""

    event_type: str = Field(
        ..., description="Type of event (created, updated, status_changed)"
    )
    timestamp: datetime = Field(..., description="When the event occurred")
    description: str = Field(..., description="Human-readable description of the event")
    details: Optional[Dict] = Field(None, description="Additional event details")


class TaskHistoryResponse(BaseModel):
    """Response model for task history"""

    task_id: int = Field(..., description="Task ID")
    task_title: str = Field(..., description="Task title")
    events: List[ActivityEvent] = Field(
        ..., description="List of activity events in chronological order"
    )


class ActivityLogResponse(BaseModel):
    """Response model for activity log entries"""

    id: int
    task_id: int
    action: str = Field(..., description="Action type: status_change, created, updated, archived")
    old_value: Optional[str] = Field(None, description="Previous value before change")
    new_value: Optional[str] = Field(None, description="New value after change")
    changed_by: int = Field(..., description="User ID who made the change")
    changed_at: datetime = Field(..., description="Timestamp of the change")

    class Config:
        from_attributes = True


class ArchiveRequest(BaseModel):
    """Request model for archiving a task"""

    reason: Optional[str] = Field(None, description="Reason for archiving the task")
