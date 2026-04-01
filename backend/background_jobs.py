"""
Background jobs for task lifecycle management.

This module provides automated maintenance functions for tasks:
- Flagging overdue tasks
- Auto-archiving stale tasks

These functions are designed to be run periodically (e.g., daily via cron job).
"""

from datetime import datetime
from sqlalchemy.orm import Session
from backend import crud
from backend.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


def run_task_maintenance():
    """
    Run periodic task maintenance operations.

    Performs two key operations:
    1. Flags overdue tasks (past due date, not completed)
    2. Auto-archives old tasks (90+ days in todo status)

    Returns:
        dict: Dictionary containing counts of tasks processed
            - overdue_flagged: Number of tasks flagged as overdue
            - auto_archived: Number of tasks automatically archived

    Example:
        >>> result = run_task_maintenance()
        >>> print(f"Flagged {result['overdue_flagged']} overdue tasks")
    """
    db = SessionLocal()
    try:
        # Flag overdue tasks
        overdue_count = crud.flag_overdue_tasks(db)
        logger.info(f"Flagged {overdue_count} tasks as overdue")

        # Auto-archive old tasks (90+ days in todo)
        archived_count = crud.auto_archive_old_tasks(db, days=90)
        logger.info(f"Auto-archived {archived_count} old tasks")

        return {"overdue_flagged": overdue_count, "auto_archived": archived_count}
    except Exception as e:
        logger.error(f"Error running task maintenance: {str(e)}")
        raise
    finally:
        db.close()
