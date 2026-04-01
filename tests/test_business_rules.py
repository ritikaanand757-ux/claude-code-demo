"""
Tests for business rule enforcement in Task Manager API.

This test suite validates:
- Ownership rules (task must have owner, only owner can modify)
- Validation rules (title length, high priority needs due date, completion notes)
- Deletion rules (cannot delete in-progress tasks)
- Activity logging (status changes are recorded)
- Overdue handling (flagging and retrieval)
- Archiving (manual and automated)
"""

import pytest
from datetime import datetime, timedelta
from fastapi import status


class TestOwnershipRules:
    """Test task ownership and permission rules"""

    def test_task_requires_owner(self, authenticated_client):
        """Task creation automatically assigns owner"""
        response = authenticated_client.post(
            "/api/tasks/", json={"title": "Test Task", "priority": "medium"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "owner_id" in data
        assert data["owner_id"] > 0

    def test_only_owner_can_change_status(self, client, test_user_data):
        """Only task owner can change task status"""
        # Create first user and task
        user1_data = test_user_data.copy()
        client.post("/api/auth/register", json=user1_data)
        login_response = client.post(
            "/api/auth/login",
            json={"email": user1_data["email"], "password": user1_data["password"]},
        )
        token1 = login_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # User 1 creates a task
        task_response = client.post(
            "/api/tasks/",
            json={"title": "Test Task"},
            headers=headers1,
        )
        task_id = task_response.json()["id"]

        # Create second user
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=user2_data)
        login_response2 = client.post(
            "/api/auth/login",
            json={"email": user2_data["email"], "password": user2_data["password"]},
        )
        token2 = login_response2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 2 tries to change status -> should fail
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=headers2,
        )
        assert response.status_code == 403
        assert "owner" in response.json()["detail"].lower()

        # User 1 changes status -> should succeed
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=headers1,
        )
        assert response.status_code == 200


class TestValidationRules:
    """Test Pydantic validation rules and business constraints"""

    def test_high_priority_requires_due_date(self, authenticated_client):
        """High priority tasks must have a due date"""
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "High Priority Task", "priority": "high"},
        )
        assert response.status_code == 422
        error_detail = str(response.json()["detail"])
        assert "due date" in error_detail.lower()

    def test_high_priority_with_due_date_succeeds(self, authenticated_client):
        """High priority task with due date should succeed"""
        future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = authenticated_client.post(
            "/api/tasks/",
            json={
                "title": "High Priority Task",
                "priority": "high",
                "due_date": future_date,
            },
        )
        assert response.status_code == 201

    def test_title_length_validation_too_short(self, authenticated_client):
        """Task title must be at least 5 characters"""
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Hi"},
        )
        assert response.status_code == 422

    def test_title_length_validation_valid(self, authenticated_client):
        """Task title with 5+ characters should succeed"""
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Valid"},
        )
        assert response.status_code == 201

    def test_title_length_validation_too_long(self, authenticated_client):
        """Task title must be at most 100 characters"""
        long_title = "x" * 101
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": long_title},
        )
        assert response.status_code == 422

    def test_done_requires_completion_note(self, authenticated_client):
        """Marking task as done requires completion note"""
        # Create task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Test Task"},
        )
        task_id = response.json()["id"]

        # Try to mark done without note
        response = authenticated_client.put(
            f"/api/tasks/{task_id}",
            json={"status": "done"},
        )
        assert response.status_code == 422
        error_detail = str(response.json()["detail"])
        assert "completion note" in error_detail.lower()

    def test_done_with_completion_note_succeeds(self, authenticated_client):
        """Marking task as done with completion note should succeed"""
        # Create task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Test Task"},
        )
        task_id = response.json()["id"]

        # Mark done with note
        response = authenticated_client.put(
            f"/api/tasks/{task_id}",
            json={"status": "done", "completion_note": "Task completed successfully"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "done"
        assert response.json()["completion_note"] == "Task completed successfully"


class TestDeletionRules:
    """Test task deletion business rules"""

    def test_cannot_delete_in_progress_task(self, authenticated_client):
        """Cannot delete tasks with in_progress status"""
        # Create in_progress task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Active Task", "status": "in_progress"},
        )
        task_id = response.json()["id"]

        # Try to delete
        response = authenticated_client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 400
        assert "in progress" in response.json()["detail"].lower()

    def test_can_delete_todo_task(self, authenticated_client):
        """Can delete tasks with todo status"""
        # Create todo task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Todo Task"},
        )
        task_id = response.json()["id"]

        # Delete should succeed
        response = authenticated_client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 204

    def test_only_owner_can_delete(self, client, test_user_data):
        """Only task owner can delete their tasks"""
        # Create first user and task
        user1_data = test_user_data.copy()
        client.post("/api/auth/register", json=user1_data)
        login_response = client.post(
            "/api/auth/login",
            json={"email": user1_data["email"], "password": user1_data["password"]},
        )
        token1 = login_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # User 1 creates a task
        task_response = client.post(
            "/api/tasks/",
            json={"title": "Test Task"},
            headers=headers1,
        )
        task_id = task_response.json()["id"]

        # Create second user
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=user2_data)
        login_response2 = client.post(
            "/api/auth/login",
            json={"email": user2_data["email"], "password": user2_data["password"]},
        )
        token2 = login_response2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 2 tries to delete -> should fail
        response = client.delete(f"/api/tasks/{task_id}", headers=headers2)
        assert response.status_code == 403
        assert "owner" in response.json()["detail"].lower()


class TestActivityLogging:
    """Test activity log creation and retrieval"""

    def test_status_change_creates_log(self, authenticated_client):
        """Status changes are automatically logged"""
        # Create task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Test Task"},
        )
        task_id = response.json()["id"]

        # Change status
        authenticated_client.put(
            f"/api/tasks/{task_id}",
            json={"status": "in_progress"},
        )

        # Check activity log
        response = authenticated_client.get(f"/api/tasks/{task_id}/activity")
        assert response.status_code == 200
        logs = response.json()
        assert len(logs) >= 2  # At least created + status_change
        assert any(log["action"] == "status_change" for log in logs)
        assert any(log["action"] == "created" for log in logs)

        # Verify status change details
        status_change_log = next(
            log for log in logs if log["action"] == "status_change"
        )
        assert status_change_log["old_value"] == "todo"
        assert status_change_log["new_value"] == "in_progress"

    def test_task_creation_logged(self, authenticated_client):
        """Task creation is logged"""
        # Create task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Test Task"},
        )
        task_id = response.json()["id"]

        # Check activity log
        response = authenticated_client.get(f"/api/tasks/{task_id}/activity")
        assert response.status_code == 200
        logs = response.json()
        assert len(logs) >= 1
        assert logs[-1]["action"] == "created"  # Most recent is first, so created is last


class TestOverdueHandling:
    """Test overdue task detection and flagging"""

    def test_overdue_endpoint_returns_past_due(self, authenticated_client):
        """Overdue endpoint returns tasks past their due date"""
        # Create overdue task
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        authenticated_client.post(
            "/api/tasks/",
            json={
                "title": "Overdue Task",
                "due_date": past_date,
                "priority": "high",
            },
        )

        # Create future task (should not appear)
        future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
        authenticated_client.post(
            "/api/tasks/",
            json={
                "title": "Future Task",
                "due_date": future_date,
                "priority": "high",
            },
        )

        # Check overdue endpoint
        response = authenticated_client.get("/api/tasks/overdue")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        assert any(task["title"] == "Overdue Task" for task in tasks)
        assert all(task["title"] != "Future Task" for task in tasks)

    def test_completed_tasks_not_overdue(self, authenticated_client):
        """Completed tasks should not appear in overdue list"""
        # Create overdue but completed task
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        response = authenticated_client.post(
            "/api/tasks/",
            json={
                "title": "Completed Overdue Task",
                "due_date": past_date,
                "priority": "high",
                "status": "done",
                "completion_note": "Done",
            },
        )

        # Check overdue endpoint - should not include completed task
        response = authenticated_client.get("/api/tasks/overdue")
        assert response.status_code == 200
        tasks = response.json()
        assert all(task["title"] != "Completed Overdue Task" for task in tasks)


class TestArchiving:
    """Test manual and automated archiving"""

    def test_manual_archive(self, authenticated_client):
        """Tasks can be manually archived"""
        # Create task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Archive Me"},
        )
        task_id = response.json()["id"]

        # Archive it
        response = authenticated_client.post(
            f"/api/tasks/{task_id}/archive",
            json={"reason": "No longer needed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_archived"] == True
        assert data["archived_at"] is not None

    def test_archived_endpoint(self, authenticated_client):
        """Archived endpoint returns archived tasks"""
        # Create and archive task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Archived Task"},
        )
        task_id = response.json()["id"]
        authenticated_client.post(
            f"/api/tasks/{task_id}/archive",
            json={"reason": "Test"},
        )

        # Check archived endpoint
        response = authenticated_client.get("/api/tasks/archived")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        assert any(task["title"] == "Archived Task" for task in tasks)
        assert all(task["is_archived"] == True for task in tasks)

    def test_archive_creates_activity_log(self, authenticated_client):
        """Archiving a task creates an activity log entry"""
        # Create task
        response = authenticated_client.post(
            "/api/tasks/",
            json={"title": "Archive Me"},
        )
        task_id = response.json()["id"]

        # Archive it
        authenticated_client.post(
            f"/api/tasks/{task_id}/archive",
            json={"reason": "Testing archive"},
        )

        # Check activity log
        response = authenticated_client.get(f"/api/tasks/{task_id}/activity")
        assert response.status_code == 200
        logs = response.json()
        assert any(log["action"] == "archived" for log in logs)

        # Verify archived log details
        archived_log = next(log for log in logs if log["action"] == "archived")
        assert "Testing archive" in archived_log["new_value"]


class TestMaintenanceJob:
    """Test automated maintenance operations"""

    def test_maintenance_endpoint_exists(self, authenticated_client):
        """Maintenance endpoint is accessible"""
        response = authenticated_client.post("/api/tasks/maintenance/run")
        assert response.status_code == 200
        data = response.json()
        assert "overdue_flagged" in data
        assert "auto_archived" in data
