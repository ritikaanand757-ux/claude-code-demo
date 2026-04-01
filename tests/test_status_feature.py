"""
Test suite for task status feature.

This module tests the newly added status field functionality including:
- Creating tasks with different statuses
- Filtering tasks by status
- Updating task status
- Status validation

Test Coverage:
    - Task creation with valid status values
    - Task creation with invalid status values (validation error)
    - Filtering by status (todo, in_progress, done, blocked)
    - Updating task status
    - Combined filtering (status + priority + completed)
"""
import pytest
from fastapi import status


class TestTaskStatus:
    """
    Test suite for task status feature.

    Tests both success cases and error cases for the status field.
    """

    def test_create_task_with_status_todo(self, client):
        """Test creating a task with status='todo' (success case)"""
        task_data = {
            "title": "New Todo Task",
            "status": "todo"
        }
        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Todo Task"
        assert data["status"] == "todo"

    def test_create_task_with_status_in_progress(self, client):
        """Test creating a task with status='in_progress' (success case)"""
        task_data = {
            "title": "Work In Progress",
            "status": "in_progress"
        }
        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "in_progress"

    def test_create_task_with_status_done(self, client):
        """Test creating a task with status='done' (success case)"""
        task_data = {
            "title": "Completed Task",
            "status": "done"
        }
        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "done"

    def test_create_task_with_status_blocked(self, client):
        """Test creating a task with status='blocked' (success case)"""
        task_data = {
            "title": "Blocked Task",
            "status": "blocked"
        }
        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "blocked"

    def test_create_task_default_status(self, client):
        """Test that default status is 'todo' when not specified"""
        task_data = {
            "title": "Task Without Status"
        }
        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "todo"  # Default value

    def test_create_task_with_invalid_status(self, client):
        """Test creating a task with invalid status fails (error case)"""
        task_data = {
            "title": "Invalid Status Task",
            "status": "invalid_status"
        }
        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_filter_tasks_by_status_todo(self, client):
        """Test filtering tasks by status='todo' (success case)"""
        # Create tasks with different statuses
        tasks = [
            {"title": "Todo 1", "status": "todo"},
            {"title": "Todo 2", "status": "todo"},
            {"title": "In Progress", "status": "in_progress"},
            {"title": "Done", "status": "done"}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by status=todo
        response = client.get("/api/tasks/?status=todo")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 2
        assert all(task["status"] == "todo" for task in data)

    def test_filter_tasks_by_status_in_progress(self, client):
        """Test filtering tasks by status='in_progress' (success case)"""
        # Create tasks
        tasks = [
            {"title": "Task 1", "status": "todo"},
            {"title": "Task 2", "status": "in_progress"},
            {"title": "Task 3", "status": "in_progress"},
            {"title": "Task 4", "status": "done"}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by status=in_progress
        response = client.get("/api/tasks/?status=in_progress")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 2
        assert all(task["status"] == "in_progress" for task in data)

    def test_filter_tasks_by_status_done(self, client):
        """Test filtering tasks by status='done' (success case)"""
        # Create tasks
        tasks = [
            {"title": "Task 1", "status": "todo"},
            {"title": "Task 2", "status": "done"},
            {"title": "Task 3", "status": "done"},
            {"title": "Task 4", "status": "done"}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by status=done
        response = client.get("/api/tasks/?status=done")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 3
        assert all(task["status"] == "done" for task in data)

    def test_filter_tasks_by_status_blocked(self, client):
        """Test filtering tasks by status='blocked' (success case)"""
        # Create tasks
        tasks = [
            {"title": "Task 1", "status": "blocked"},
            {"title": "Task 2", "status": "todo"},
            {"title": "Task 3", "status": "blocked"}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by status=blocked
        response = client.get("/api/tasks/?status=blocked")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 2
        assert all(task["status"] == "blocked" for task in data)

    def test_filter_with_invalid_status(self, client):
        """Test filtering with invalid status value fails (error case)"""
        response = client.get("/api/tasks/?status=invalid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_task_status(self, client):
        """Test updating task status (success case)"""
        # Create a task
        task_data = {"title": "Task to Update", "status": "todo"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update status to in_progress
        update_data = {"status": "in_progress"}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["title"] == "Task to Update"  # Other fields unchanged

    def test_update_task_status_to_done(self, client):
        """Test updating task status to done (success case)"""
        # Create a task
        task_data = {"title": "Task", "status": "in_progress"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update to done
        update_data = {"status": "done"}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "done"

    def test_update_task_with_invalid_status(self, client):
        """Test updating task with invalid status fails (error case)"""
        # Create a task
        task_data = {"title": "Task"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Try to update with invalid status
        update_data = {"status": "pending"}  # Invalid status
        response = client.put(f"/api/tasks/{task_id}", json=update_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_combined_filters_status_and_priority(self, client):
        """Test filtering by both status and priority (success case)"""
        # Create tasks with various combinations
        tasks = [
            {"title": "High Todo", "priority": "high", "status": "todo"},
            {"title": "High In Progress", "priority": "high", "status": "in_progress"},
            {"title": "Low Todo", "priority": "low", "status": "todo"},
            {"title": "Medium Done", "priority": "medium", "status": "done"}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by high priority AND todo status
        response = client.get("/api/tasks/?priority=high&status=todo")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"
        assert data[0]["status"] == "todo"

    def test_combined_filters_status_priority_completed(self, client):
        """Test filtering by status, priority, and completed (success case)"""
        # Create tasks
        tasks = [
            {"title": "T1", "priority": "high", "status": "done", "completed": True},
            {"title": "T2", "priority": "high", "status": "done", "completed": False},
            {"title": "T3", "priority": "high", "status": "todo", "completed": False}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by high priority, done status, and completed
        response = client.get("/api/tasks/?priority=high&status=done&completed=true")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"
        assert data[0]["status"] == "done"
        assert data[0]["completed"] is True

    def test_complete_status_workflow(self, client):
        """Test complete workflow: todo -> in_progress -> done (success case)"""
        # 1. Create task with status=todo
        task_data = {"title": "Workflow Task", "status": "todo"}
        create_response = client.post("/api/tasks/", json=task_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        task_id = create_response.json()["id"]

        # 2. Verify it's in todo status
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.json()["status"] == "todo"

        # 3. Update to in_progress
        update1 = client.put(f"/api/tasks/{task_id}", json={"status": "in_progress"})
        assert update1.status_code == status.HTTP_200_OK
        assert update1.json()["status"] == "in_progress"

        # 4. Update to done
        update2 = client.put(f"/api/tasks/{task_id}", json={"status": "done"})
        assert update2.status_code == status.HTTP_200_OK
        assert update2.json()["status"] == "done"

        # 5. Mark as completed
        update3 = client.put(f"/api/tasks/{task_id}", json={"completed": True})
        assert update3.status_code == status.HTTP_200_OK
        final = update3.json()
        assert final["status"] == "done"
        assert final["completed"] is True
