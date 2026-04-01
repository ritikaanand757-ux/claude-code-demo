"""
Test suite for basic Task Manager API endpoints.

This module contains comprehensive tests for all CRUD operations on the Task API,
including edge cases, error handling, and pagination functionality.

Test Coverage:
    - Root and health check endpoints
    - Task creation (with and without optional fields)
    - Task retrieval (single and multiple)
    - Task updates (full and partial)
    - Task deletion
    - Pagination functionality
    - Error cases (404, 422)
"""
import pytest
from fastapi import status


class TestTaskAPI:
    """
    Test suite for Task API endpoints.

    This class contains all test cases for basic CRUD operations on tasks,
    testing both successful operations and error conditions.
    """

    def test_read_root(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_get_empty_tasks(self, client):
        """Test getting tasks when database is empty"""
        response = client.get("/api/tasks/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_task(self, client):
        """Test creating a new task"""
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "completed": False
        }
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["completed"] == task_data["completed"]
        assert "id" in data
        assert "created_at" in data

    def test_create_task_without_description(self, client):
        """Test creating a task without description"""
        task_data = {
            "title": "Test Task Without Description",
            "completed": False
        }
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] is None

    def test_create_task_missing_title(self, client):
        """Test creating a task without a title (should fail)"""
        task_data = {
            "description": "Task without title",
            "completed": False
        }
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_tasks(self, client):
        """Test getting all tasks"""
        # Create multiple tasks
        tasks = [
            {"title": "Task 1", "description": "Description 1", "completed": False},
            {"title": "Task 2", "description": "Description 2", "completed": True},
            {"title": "Task 3", "completed": False}
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Get all tasks
        response = client.get("/api/tasks/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 3
        assert data[0]["title"] == "Task 1"
        assert data[1]["title"] == "Task 2"
        assert data[2]["title"] == "Task 3"

    def test_get_task_by_id(self, client):
        """Test getting a specific task by ID"""
        # Create a task
        task_data = {"title": "Test Task", "description": "Test Description"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Get the task by ID
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]

    def test_get_nonexistent_task(self, client):
        """Test getting a task that doesn't exist"""
        response = client.get("/api/tasks/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task(self, client):
        """Test updating a task"""
        # Create a task
        task_data = {"title": "Original Title", "description": "Original Description"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update the task
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "completed": True
        }
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["completed"] == update_data["completed"]

    def test_update_task_partial(self, client):
        """Test partially updating a task"""
        # Create a task
        task_data = {"title": "Original Title", "description": "Original Description"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update only the completed status
        update_data = {"completed": True}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["title"] == task_data["title"]  # Should remain unchanged
        assert data["description"] == task_data["description"]  # Should remain unchanged
        assert data["completed"] is True  # Should be updated

    def test_update_nonexistent_task(self, client):
        """Test updating a task that doesn't exist"""
        update_data = {"title": "Updated Title"}
        response = client.put("/api/tasks/9999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

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
        """Test deleting a task that doesn't exist"""
        response = client.delete("/api/tasks/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_task_pagination(self, client):
        """Test task pagination with skip and limit"""
        # Create 10 tasks
        for i in range(10):
            client.post("/api/tasks/", json={"title": f"Task {i}"})

        # Test with limit
        response = client.get("/api/tasks/?limit=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with skip
        response = client.get("/api/tasks/?skip=5&limit=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5
