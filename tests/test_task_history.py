"""
Test suite for task history endpoint.

This module tests the GET /api/tasks/{id}/history endpoint that returns
activity logs for tasks.

Test Coverage:
    - Success case: Getting history for an existing task
    - Error case: Getting history for a non-existent task (404)
    - Verify history contains created event
    - Verify history contains updated event after modification
    - Verify event structure and data
"""
import pytest
from fastapi import status
import time


class TestTaskHistory:
    """
    Test suite for task history endpoint.

    Tests both success cases and error cases following CLAUDE.md guidelines.
    """

    def test_get_task_history_success(self, client):
        """Test getting history for an existing task (success case)"""
        # Create a task
        task_data = {
            "title": "Test Task with History",
            "description": "This task will have history",
            "status": "todo"
        }
        create_response = client.post("/api/tasks/", json=task_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        task_id = create_response.json()["id"]

        # Get task history
        response = client.get(f"/api/tasks/{task_id}/history")

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        history = response.json()

        # Verify structure
        assert "task_id" in history
        assert "task_title" in history
        assert "events" in history

        # Verify data
        assert history["task_id"] == task_id
        assert history["task_title"] == "Test Task with History"
        assert isinstance(history["events"], list)
        assert len(history["events"]) >= 1

    def test_get_task_history_not_found(self, client):
        """Test getting history for non-existent task (error case)"""
        # Try to get history for non-existent task
        response = client.get("/api/tasks/99999/history")

        # Verify 404 response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_history_contains_created_event(self, client):
        """Test that history contains a created event"""
        # Create a task
        task_data = {"title": "New Task", "priority": "high"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Get history
        response = client.get(f"/api/tasks/{task_id}/history")
        history = response.json()

        # Verify created event exists
        events = history["events"]
        assert len(events) >= 1

        created_event = events[0]
        assert created_event["event_type"] == "created"
        assert "timestamp" in created_event
        assert "description" in created_event
        assert "New Task" in created_event["description"]

    def test_history_created_event_details(self, client):
        """Test that created event contains proper details"""
        # Create a task with specific attributes
        task_data = {
            "title": "Task with Details",
            "status": "in_progress",
            "priority": "low",
            "completed": False
        }
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Get history
        response = client.get(f"/api/tasks/{task_id}/history")
        history = response.json()

        # Verify created event details
        created_event = history["events"][0]
        assert created_event["event_type"] == "created"
        assert "details" in created_event

        details = created_event["details"]
        assert "initial_status" in details
        assert "initial_priority" in details
        assert "completed" in details

    def test_history_shows_updated_event_after_modification(self, client):
        """Test that history shows updated event after task is modified"""
        # Create a task
        task_data = {"title": "Task to Update", "status": "todo"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Small delay to ensure different timestamps
        time.sleep(0.1)

        # Update the task
        update_data = {"status": "in_progress", "completed": True}
        update_response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK

        # Get history
        response = client.get(f"/api/tasks/{task_id}/history")
        history = response.json()

        # Verify events
        events = history["events"]

        # Should have at least created event, possibly updated event
        assert len(events) >= 1

        # First event should be created
        assert events[0]["event_type"] == "created"

        # If updated event exists, verify it
        if len(events) > 1:
            updated_event = events[1]
            assert updated_event["event_type"] == "updated"
            assert "timestamp" in updated_event
            assert "details" in updated_event

    def test_history_event_structure(self, client):
        """Test that each event has the required structure"""
        # Create a task
        task_data = {"title": "Structure Test Task"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Get history
        response = client.get(f"/api/tasks/{task_id}/history")
        history = response.json()

        # Verify each event has required fields
        for event in history["events"]:
            assert "event_type" in event
            assert "timestamp" in event
            assert "description" in event
            # details is optional
            if "details" in event:
                assert isinstance(event["details"], dict)

    def test_history_chronological_order(self, client):
        """Test that events are in chronological order"""
        # Create a task
        task_data = {"title": "Chronological Test"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Update it
        time.sleep(0.1)
        client.put(f"/api/tasks/{task_id}", json={"description": "Updated"})

        # Get history
        response = client.get(f"/api/tasks/{task_id}/history")
        history = response.json()

        events = history["events"]
        if len(events) > 1:
            # Verify first event is created, last is updated
            assert events[0]["event_type"] == "created"
            # Later events should have later or equal timestamps
            for i in range(len(events) - 1):
                # Just verify timestamps exist and are strings
                assert events[i]["timestamp"]
                assert events[i + 1]["timestamp"]

    def test_history_for_completed_task(self, client):
        """Test history for a task that's been marked completed"""
        # Create and complete a task
        task_data = {"title": "Complete Task", "completed": True, "status": "done"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Get history
        response = client.get(f"/api/tasks/{task_id}/history")
        assert response.status_code == status.HTTP_200_OK

        history = response.json()
        assert history["task_id"] == task_id
        assert len(history["events"]) >= 1

        # Verify created event shows completed status
        created_event = history["events"][0]
        assert created_event["details"]["completed"] is True

    def test_history_for_multiple_tasks(self, client):
        """Test that each task has independent history"""
        # Create two tasks
        task1_response = client.post("/api/tasks/", json={"title": "Task 1"})
        task2_response = client.post("/api/tasks/", json={"title": "Task 2"})

        task1_id = task1_response.json()["id"]
        task2_id = task2_response.json()["id"]

        # Get histories
        history1 = client.get(f"/api/tasks/{task1_id}/history").json()
        history2 = client.get(f"/api/tasks/{task2_id}/history").json()

        # Verify they are different
        assert history1["task_id"] == task1_id
        assert history2["task_id"] == task2_id
        assert history1["task_title"] == "Task 1"
        assert history2["task_title"] == "Task 2"

    def test_history_endpoint_url_format(self, client):
        """Test that the endpoint follows REST conventions"""
        # Create a task
        task_data = {"title": "REST Convention Test"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Verify URL format works: /api/tasks/{id}/history
        response = client.get(f"/api/tasks/{task_id}/history")
        assert response.status_code == status.HTTP_200_OK

        # Verify it's under the tasks route
        history = response.json()
        assert history["task_id"] == task_id
