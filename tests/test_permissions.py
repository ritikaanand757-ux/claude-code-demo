"""
Test suite for task permission system (update and delete operations)

This module tests the permission rules for:
- Regular users can only edit/delete their own tasks
- Admins can edit/delete any tasks
- In-progress tasks can only be deleted by admins
"""

import pytest
from backend.models import User


@pytest.fixture
def setup_users_and_tasks(client, db_session):
    """
    Setup test data: 2 regular users, 1 admin, and tasks owned by each
    """
    # Create regular user 1
    user1_data = {
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123",
    }
    response = client.post("/api/auth/register", json=user1_data)
    assert response.status_code == 201
    user1 = response.json()

    # Login as user1 and get token
    login_response = client.post(
        "/api/auth/login",
        json={"email": "user1@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    user1_token = login_response.json()["access_token"]

    # Create task owned by user1
    task1_response = client.post(
        "/api/tasks/",
        json={"title": "User1 Task", "status": "todo"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert task1_response.status_code == 201
    task1 = task1_response.json()

    # Create in-progress task owned by user1
    task_in_progress_response = client.post(
        "/api/tasks/",
        json={"title": "User1 In Progress", "status": "in_progress"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert task_in_progress_response.status_code == 201
    task_in_progress = task_in_progress_response.json()

    # Create regular user 2
    user2_data = {
        "username": "user2",
        "email": "user2@example.com",
        "password": "password123",
    }
    response = client.post("/api/auth/register", json=user2_data)
    assert response.status_code == 201
    user2 = response.json()

    # Login as user2 and get token
    login_response = client.post(
        "/api/auth/login",
        json={"email": "user2@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    user2_token = login_response.json()["access_token"]

    # Create task owned by user2
    task2_response = client.post(
        "/api/tasks/",
        json={"title": "User2 Task", "status": "todo"},
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    assert task2_response.status_code == 201
    task2 = task2_response.json()

    # Create admin user
    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpass123",
    }
    response = client.post("/api/auth/register", json=admin_data)
    assert response.status_code == 201

    # Make the admin user actually an admin by updating database
    admin_user = db_session.query(User).filter(User.username == "admin").first()
    admin_user.is_admin = True
    db_session.commit()

    # Login as admin and get token
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]

    return {
        "user1": {"id": user1["id"], "token": user1_token, "task_id": task1["id"], "task_in_progress_id": task_in_progress["id"]},
        "user2": {"id": user2["id"], "token": user2_token, "task_id": task2["id"]},
        "admin": {"token": admin_token},
    }


# ============== UPDATE PERMISSION TESTS ==============


def test_user_can_update_own_task(client, setup_users_and_tasks):
    """Test that a user can update their own task"""
    data = setup_users_and_tasks
    user1_token = data["user1"]["token"]
    task1_id = data["user1"]["task_id"]

    # Update own task
    response = client.put(
        f"/api/tasks/{task1_id}",
        json={"title": "Updated Task Title"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task Title"


def test_user_cannot_update_other_users_task(client, setup_users_and_tasks):
    """Test that a user cannot update another user's task"""
    data = setup_users_and_tasks
    user1_token = data["user1"]["token"]
    task2_id = data["user2"]["task_id"]  # Task owned by user2

    # Try to update user2's task as user1
    response = client.put(
        f"/api/tasks/{task2_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    assert response.status_code == 403
    assert "Only task owner can update this task" in response.json()["detail"]


def test_admin_can_update_any_task(client, setup_users_and_tasks):
    """Test that an admin can update any user's task"""
    data = setup_users_and_tasks
    admin_token = data["admin"]["token"]
    task1_id = data["user1"]["task_id"]  # Task owned by user1

    # Update user1's task as admin
    response = client.put(
        f"/api/tasks/{task1_id}",
        json={"title": "Admin Updated Title"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Admin Updated Title"


# ============== DELETE PERMISSION TESTS ==============


def test_user_can_delete_own_task(client, setup_users_and_tasks):
    """Test that a user can delete their own task"""
    data = setup_users_and_tasks
    user1_token = data["user1"]["token"]
    task1_id = data["user1"]["task_id"]

    # Delete own task
    response = client.delete(
        f"/api/tasks/{task1_id}",
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    assert response.status_code == 204

    # Verify task is deleted
    get_response = client.get(
        f"/api/tasks/{task1_id}",
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert get_response.status_code == 404


def test_user_cannot_delete_other_users_task(client, setup_users_and_tasks):
    """Test that a user cannot delete another user's task"""
    data = setup_users_and_tasks
    user1_token = data["user1"]["token"]
    task2_id = data["user2"]["task_id"]  # Task owned by user2

    # Try to delete user2's task as user1
    response = client.delete(
        f"/api/tasks/{task2_id}",
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    assert response.status_code == 403
    assert "Only task owner can delete" in response.json()["detail"]


def test_user_cannot_delete_in_progress_task(client, setup_users_and_tasks):
    """Test that a regular user cannot delete their own in-progress task"""
    data = setup_users_and_tasks
    user1_token = data["user1"]["token"]
    task_in_progress_id = data["user1"]["task_in_progress_id"]

    # Try to delete own in-progress task
    response = client.delete(
        f"/api/tasks/{task_in_progress_id}",
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    assert response.status_code == 400
    assert "Cannot delete tasks that are in progress" in response.json()["detail"]


def test_admin_can_delete_any_task(client, setup_users_and_tasks):
    """Test that an admin can delete any user's task"""
    data = setup_users_and_tasks
    admin_token = data["admin"]["token"]
    task1_id = data["user1"]["task_id"]  # Task owned by user1

    # Delete user1's task as admin
    response = client.delete(
        f"/api/tasks/{task1_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204


def test_admin_can_delete_in_progress_task(client, setup_users_and_tasks):
    """Test that an admin can delete in-progress tasks"""
    data = setup_users_and_tasks
    admin_token = data["admin"]["token"]
    task_in_progress_id = data["user1"]["task_in_progress_id"]

    # Delete in-progress task as admin
    response = client.delete(
        f"/api/tasks/{task_in_progress_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204


# ============== EDGE CASE TESTS ==============


def test_update_nonexistent_task_returns_404(client, setup_users_and_tasks):
    """Test that updating a non-existent task returns 404"""
    data = setup_users_and_tasks
    user1_token = data["user1"]["token"]

    response = client.put(
        "/api/tasks/99999",
        json={"title": "New Title"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    assert response.status_code == 404


def test_delete_nonexistent_task_returns_404(client, setup_users_and_tasks):
    """Test that deleting a non-existent task returns 404"""
    data = setup_users_and_tasks
    user1_token = data["user1"]["token"]

    response = client.delete(
        "/api/tasks/99999",
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    assert response.status_code == 404


def test_unauthorized_update_returns_401(client):
    """Test that updating without authentication returns 401"""
    response = client.put("/api/tasks/1", json={"title": "New Title"})
    assert response.status_code == 401


def test_unauthorized_delete_returns_401(client):
    """Test that deleting without authentication returns 401"""
    response = client.delete("/api/tasks/1")
    assert response.status_code == 401
