"""
Test suite for refactored API with CRUD separation and new endpoints.

This module tests the refactored API structure where business logic is separated
into CRUD operations, along with newly added advanced endpoints.

Test Coverage:
    - Search functionality across multiple fields
    - Statistics endpoint for task analytics
    - Bulk delete operations
    - Advanced pagination with page parameter
    - Combined filtering and pagination
    - CRUD separation architecture
    - Integration tests for complete workflows

New Endpoints Tested:
    - GET /api/tasks/search - Full-text search
    - GET /api/tasks/stats - Task statistics
    - POST /api/tasks/bulk/delete - Bulk deletion
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestRefactoredAPI:
    """
    Test suite for refactored API structure.

    This class verifies that the refactored code structure (with CRUD separation)
    works correctly and tests all new advanced endpoints including search,
    statistics, and bulk operations.
    """

    def test_search_tasks(self, client):
        """Test search endpoint"""
        # Create tasks with searchable content
        tasks = [
            {"title": "Fix urgent bug in authentication", "tags": "bug, urgent"},
            {"title": "Add new feature for dashboard", "tags": "feature"},
            {"title": "Update documentation", "description": "Update API documentation"},
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        # Search by title
        response = client.get("/api/tasks/search?q=bug")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any("bug" in task["title"].lower() or (task["tags"] and "bug" in task["tags"].lower()) for task in data)

        # Search by tag
        response = client.get("/api/tasks/search?q=feature")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

        # Search by description
        response = client.get("/api/tasks/search?q=documentation")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_search_no_results(self, client):
        """Test search with no matching results"""
        client.post("/api/tasks/", json={"title": "Test Task"})

        response = client.get("/api/tasks/search?q=nonexistent")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_search_empty_query(self, client):
        """Test search with empty query fails validation"""
        response = client.get("/api/tasks/search?q=")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_statistics(self, client):
        """Test statistics endpoint"""
        # Create tasks with different statuses and priorities
        tasks = [
            {"title": "Task 1", "priority": "high", "completed": True},
            {"title": "Task 2", "priority": "high", "completed": False},
            {"title": "Task 3", "priority": "medium", "completed": True},
            {"title": "Task 4", "priority": "medium", "completed": False},
            {"title": "Task 5", "priority": "low", "completed": False},
        ]

        for task in tasks:
            client.post("/api/tasks/", json=task)

        response = client.get("/api/tasks/stats")
        assert response.status_code == status.HTTP_200_OK

        stats = response.json()
        assert stats["total"] == 5
        assert stats["completed"] == 2
        assert stats["pending"] == 3
        assert stats["by_priority"]["high"] == 2
        assert stats["by_priority"]["medium"] == 2
        assert stats["by_priority"]["low"] == 1

    def test_statistics_empty_database(self, client):
        """Test statistics with empty database"""
        response = client.get("/api/tasks/stats")
        assert response.status_code == status.HTTP_200_OK

        stats = response.json()
        assert stats["total"] == 0
        assert stats["completed"] == 0
        assert stats["pending"] == 0
        assert stats["by_priority"]["high"] == 0
        assert stats["by_priority"]["medium"] == 0
        assert stats["by_priority"]["low"] == 0

    def test_bulk_delete(self, client):
        """Test bulk delete endpoint"""
        # Create multiple tasks
        task_ids = []
        for i in range(5):
            response = client.post("/api/tasks/", json={"title": f"Task {i}"})
            task_ids.append(response.json()["id"])

        # Delete 3 tasks
        delete_ids = task_ids[:3]
        response = client.post("/api/tasks/bulk/delete", json={"task_ids": delete_ids})
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["deleted_count"] == 3
        assert data["requested_count"] == 3

        # Verify tasks were deleted
        for task_id in delete_ids:
            response = client.get(f"/api/tasks/{task_id}")
            assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify other tasks still exist
        for task_id in task_ids[3:]:
            response = client.get(f"/api/tasks/{task_id}")
            assert response.status_code == status.HTTP_200_OK

    def test_bulk_delete_empty_list(self, client):
        """Test bulk delete with empty list fails"""
        response = client.post("/api/tasks/bulk/delete", json={"task_ids": []})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_delete_nonexistent_ids(self, client):
        """Test bulk delete with non-existent IDs"""
        response = client.post("/api/tasks/bulk/delete", json={"task_ids": [9999, 10000]})
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["deleted_count"] == 0
        assert data["requested_count"] == 2

    def test_pagination_with_page_parameter(self, client):
        """Test pagination using page parameter"""
        # Create 25 tasks
        for i in range(25):
            client.post("/api/tasks/", json={"title": f"Task {i:02d}"})

        # Get page 1 (first 20 tasks)
        response = client.get("/api/tasks/?page=1&limit=10")
        assert response.status_code == status.HTTP_200_OK
        page1 = response.json()
        assert len(page1) == 10

        # Get page 2 (next 10 tasks)
        response = client.get("/api/tasks/?page=2&limit=10")
        assert response.status_code == status.HTTP_200_OK
        page2 = response.json()
        assert len(page2) == 10

        # Verify pages have different tasks
        page1_ids = {task["id"] for task in page1}
        page2_ids = {task["id"] for task in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

        # Get page 3 (remaining 5 tasks)
        response = client.get("/api/tasks/?page=3&limit=10")
        assert response.status_code == status.HTTP_200_OK
        page3 = response.json()
        assert len(page3) == 5

    def test_pagination_default_limit(self, client):
        """Test pagination with default limit"""
        # Create 25 tasks
        for i in range(25):
            client.post("/api/tasks/", json={"title": f"Task {i}"})

        # Get first page without specifying limit (should use default)
        response = client.get("/api/tasks/?page=1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 20  # Default limit

    def test_filter_and_pagination_combined(self, client):
        """Test combining filters with pagination"""
        # Create tasks with different priorities
        for i in range(15):
            priority = "high" if i < 5 else "medium" if i < 10 else "low"
            client.post("/api/tasks/", json={"title": f"Task {i}", "priority": priority})

        # Filter by high priority with pagination
        response = client.get("/api/tasks/?priority=high&page=1&limit=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert all(task["priority"] == "high" for task in data)

    def test_crud_separation(self, client):
        """Test that CRUD operations work correctly (routes use crud module)"""
        # This test verifies the refactored structure works end-to-end

        # Create
        task_data = {"title": "Test CRUD", "priority": "high"}
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == status.HTTP_201_CREATED
        task = response.json()
        task_id = task["id"]

        # Read
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Test CRUD"

        # Update
        response = client.put(f"/api/tasks/{task_id}", json={"priority": "low"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["priority"] == "low"

        # Delete
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_search_with_limit(self, client):
        """Test search endpoint respects limit parameter"""
        # Create many tasks with same keyword
        for i in range(60):
            client.post("/api/tasks/", json={"title": f"Important task {i}"})

        # Search with default limit (50)
        response = client.get("/api/tasks/search?q=important")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 50

        # Search with custom limit
        response = client.get("/api/tasks/search?q=important&limit=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 10

    def test_statistics_updates_after_changes(self, client):
        """Test that statistics update correctly after task changes"""
        # Initial state
        response = client.get("/api/tasks/stats")
        initial_stats = response.json()

        # Add a task
        task_data = {"title": "New Task", "priority": "high", "completed": False}
        response = client.post("/api/tasks/", json=task_data)
        task_id = response.json()["id"]

        # Check stats updated
        response = client.get("/api/tasks/stats")
        stats = response.json()
        assert stats["total"] == initial_stats["total"] + 1
        assert stats["pending"] == initial_stats["pending"] + 1
        assert stats["by_priority"]["high"] == initial_stats["by_priority"]["high"] + 1

        # Mark as completed
        client.put(f"/api/tasks/{task_id}", json={"completed": True})

        # Check stats updated again
        response = client.get("/api/tasks/stats")
        stats = response.json()
        assert stats["completed"] == initial_stats["completed"] + 1
        assert stats["pending"] == initial_stats["pending"]

    def test_all_new_endpoints_documented(self, client):
        """Test that all new endpoints are accessible"""
        # This ensures all new endpoints are properly registered

        endpoints_to_test = [
            ("/api/tasks/search?q=test", "GET"),
            ("/api/tasks/stats", "GET"),
            ("/api/tasks/bulk/delete", "POST"),
        ]

        for endpoint, method in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                if "bulk" in endpoint:
                    response = client.post(endpoint, json={"task_ids": [1]})
                else:
                    response = client.post(endpoint, json={})

            # Should not return 404 or 405 (endpoint exists and method allowed)
            assert response.status_code not in [404, 405]

    def test_complete_workflow_with_new_features(self, client):
        """Test complete workflow using all new features"""
        # 1. Check initial statistics
        response = client.get("/api/tasks/stats")
        assert response.status_code == status.HTTP_200_OK

        # 2. Create multiple tasks
        task_ids = []
        for i in range(10):
            task_data = {
                "title": f"Feature {i}",
                "description": "Implementation details",
                "priority": ["high", "medium", "low"][i % 3],
                "tags": "feature, v2.0"
            }
            response = client.post("/api/tasks/", json=task_data)
            task_ids.append(response.json()["id"])

        # 3. Search for tasks
        response = client.get("/api/tasks/search?q=feature")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 10

        # 4. Get paginated results
        response = client.get("/api/tasks/?page=1&limit=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # 5. Check updated statistics
        response = client.get("/api/tasks/stats")
        stats = response.json()
        assert stats["total"] == 10

        # 6. Bulk delete some tasks
        response = client.post("/api/tasks/bulk/delete", json={"task_ids": task_ids[:5]})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["deleted_count"] == 5

        # 7. Verify final statistics
        response = client.get("/api/tasks/stats")
        stats = response.json()
        assert stats["total"] == 5
