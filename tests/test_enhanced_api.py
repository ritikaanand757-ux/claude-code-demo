import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestEnhancedTaskAPI:
    """Comprehensive test suite for enhanced Task API with priority, tags, and due dates"""

    def test_get_empty_tasks(self, client):
        """Test getting tasks when database is empty"""
        response = client.get("/api/tasks/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_task_with_all_fields(self, client):
        """Test creating a task with all fields including priority, tags, and due date"""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Complete Project",
            "description": "Finish the task manager project",
            "completed": False,
            "priority": "high",
            "tags": "bug, urgent",
            "due_date": due_date
        }
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["completed"] == task_data["completed"]
        assert data["priority"] == "high"
        assert data["tags"] == "bug, urgent"
        assert data["due_date"] is not None
        assert "id" in data
        assert "created_at" in data

    def test_create_task_with_priority_only(self, client):
        """Test creating a task with only priority specified"""
        task_data = {
            "title": "Medium Priority Task",
            "priority": "medium"
        }
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["priority"] == "medium"
        assert data["title"] == "Medium Priority Task"

    def test_create_task_with_invalid_priority(self, client):
        """Test creating a task with invalid priority value"""
        task_data = {
            "title": "Invalid Priority Task",
            "priority": "super-high"  # Invalid priority
        }
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_without_title(self, client):
        """Test that creating a task without title fails"""
        task_data = {
            "description": "Task without title",
            "priority": "low"
        }
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_tasks_with_data(self, client):
        """Test getting tasks when tasks exist in database"""
        # Create multiple tasks
        tasks = [
            {"title": "Task 1", "priority": "high", "completed": False},
            {"title": "Task 2", "priority": "medium", "completed": True},
            {"title": "Task 3", "priority": "low", "completed": False}
        ]

        for task in tasks:
            response = client.post("/api/tasks/", json=task)
            assert response.status_code == status.HTTP_201_CREATED

        # Get all tasks
        response = client.get("/api/tasks/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_filter_tasks_by_priority(self, client):
        """Test filtering tasks by priority"""
        # Create tasks with different priorities
        tasks = [
            {"title": "High Priority 1", "priority": "high"},
            {"title": "High Priority 2", "priority": "high"},
            {"title": "Medium Priority", "priority": "medium"},
            {"title": "Low Priority", "priority": "low"}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by high priority
        response = client.get("/api/tasks/?priority=high")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(task["priority"] == "high" for task in data)

    def test_filter_tasks_by_completed_status(self, client):
        """Test filtering tasks by completion status"""
        # Create tasks with different completion statuses
        tasks = [
            {"title": "Completed Task 1", "completed": True},
            {"title": "Completed Task 2", "completed": True},
            {"title": "Pending Task", "completed": False}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by completed status
        response = client.get("/api/tasks/?completed=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(task["completed"] is True for task in data)

        # Filter by not completed status
        response = client.get("/api/tasks/?completed=false")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["completed"] is False

    def test_filter_tasks_by_priority_and_status(self, client):
        """Test filtering tasks by both priority and completion status"""
        tasks = [
            {"title": "High Completed", "priority": "high", "completed": True},
            {"title": "High Pending", "priority": "high", "completed": False},
            {"title": "Low Completed", "priority": "low", "completed": True},
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Filter by high priority AND completed
        response = client.get("/api/tasks/?priority=high&completed=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"
        assert data[0]["completed"] is True

    def test_get_task_by_id(self, client):
        """Test getting a specific task by ID"""
        # Create a task
        task_data = {
            "title": "Test Task",
            "priority": "medium",
            "tags": "test"
        }
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Get the task by ID
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == task_data["title"]
        assert data["priority"] == "medium"

    def test_get_nonexistent_task(self, client):
        """Test getting a task that doesn't exist returns 404"""
        response = client.get("/api/tasks/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_update_task_priority(self, client):
        """Test updating task priority"""
        # Create a task
        task_data = {"title": "Task to Update", "priority": "low"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update priority
        update_data = {"priority": "high"}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["priority"] == "high"
        assert data["title"] == "Task to Update"  # Title unchanged

    def test_update_task_tags(self, client):
        """Test updating task tags"""
        # Create a task
        task_data = {"title": "Task with Tags", "tags": "old-tag"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update tags
        update_data = {"tags": "new-tag, updated"}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["tags"] == "new-tag, updated"

    def test_update_task_due_date(self, client):
        """Test updating task due date"""
        # Create a task
        task_data = {"title": "Task with Due Date"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update due date
        new_due_date = (datetime.now() + timedelta(days=3)).isoformat()
        update_data = {"due_date": new_due_date}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["due_date"] is not None

    def test_update_task_completion_status(self, client):
        """Test updating task completion status"""
        # Create a task
        task_data = {"title": "Task to Complete", "completed": False}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Mark as completed
        update_data = {"completed": True}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["completed"] is True

    def test_update_nonexistent_task(self, client):
        """Test updating a task that doesn't exist returns 404"""
        update_data = {"title": "Updated Title"}
        response = client.put("/api/tasks/99999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_with_invalid_priority(self, client):
        """Test updating task with invalid priority fails"""
        # Create a task
        task_data = {"title": "Task"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Try to update with invalid priority
        update_data = {"priority": "extreme"}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_task(self, client):
        """Test deleting a task"""
        # Create a task
        task_data = {"title": "Task to Delete"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify task is deleted
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist returns 404"""
        response = client.delete("/api/tasks/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_pagination(self, client):
        """Test task pagination with skip and limit"""
        # Create 10 tasks
        for i in range(10):
            client.post("/api/tasks/", json={"title": f"Task {i}", "priority": "medium"})

        # Test with limit
        response = client.get("/api/tasks/?limit=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with skip and limit
        response = client.get("/api/tasks/?skip=5&limit=3")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    def test_create_task_default_priority(self, client):
        """Test that default priority is 'medium' if not specified"""
        task_data = {"title": "Task with Default Priority"}
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["priority"] == "medium"

    def test_filter_with_invalid_priority(self, client):
        """Test filtering with invalid priority value"""
        response = client.get("/api/tasks/?priority=invalid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_complete_workflow(self, client):
        """Test complete CRUD workflow for a task"""
        # 1. Create a task
        task_data = {
            "title": "Complete Workflow Test",
            "description": "Testing full lifecycle",
            "priority": "high",
            "tags": "test, workflow",
            "completed": False
        }
        create_response = client.post("/api/tasks/", json=task_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        task_id = create_response.json()["id"]

        # 2. Read the task
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["title"] == "Complete Workflow Test"

        # 3. Update the task
        update_data = {"completed": True, "priority": "low"}
        update_response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["completed"] is True
        assert update_response.json()["priority"] == "low"

        # 4. Delete the task
        delete_response = client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 5. Verify deletion
        final_get_response = client.get(f"/api/tasks/{task_id}")
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
