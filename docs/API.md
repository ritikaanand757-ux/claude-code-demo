# Task Manager API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000`
**API Prefix:** `/api`

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Status Codes](#status-codes)
- [Endpoints](#endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
    - [Register User](#register-user)
    - [Login](#login)
    - [Get Current User](#get-current-user)
  - [Health Check](#health-check)
  - [Task Endpoints](#task-endpoints)
    - [Get All Tasks](#get-all-tasks)
    - [Get Single Task](#get-single-task)
    - [Create Task](#create-task)
    - [Update Task](#update-task)
    - [Delete Task](#delete-task)
    - [Search Tasks](#search-tasks)
    - [Get Statistics](#get-statistics)
    - [Bulk Delete Tasks](#bulk-delete-tasks)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Overview

The Task Manager API is a RESTful API built with FastAPI that provides comprehensive task management functionality. It supports CRUD operations, advanced search, filtering, pagination, and bulk operations.

### Key Features

- **Full CRUD operations** for task management
- **Advanced filtering** by priority, completion status
- **Full-text search** across title, description, and tags
- **Pagination support** with skip/limit and page-based pagination
- **Task statistics** for analytics
- **Bulk operations** for efficiency
- **Automatic API documentation** at `/docs` and `/redoc`

---

## Authentication

The Task Manager API uses JWT (JSON Web Token) based authentication to secure user data and ensure that users can only access their own tasks.

### Authentication Flow

1. **Register** - Create a new user account
2. **Login** - Receive a JWT access token
3. **Use Token** - Include token in Authorization header for all protected endpoints
4. **Token Expiration** - Tokens expire after 30 minutes (configurable)

### Token Format

All authenticated requests must include the JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

**Example:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huIiwiZXhwIjoxNzA5MzE2MDAwfQ.abc123...
```

### Protected Endpoints

The following endpoints require authentication:

- `GET /api/tasks/` - Get all tasks (user's own tasks only)
- `GET /api/tasks/{task_id}` - Get single task
- `POST /api/tasks/` - Create task
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task
- `GET /api/tasks/search` - Search tasks
- `GET /api/tasks/stats` - Get statistics
- `POST /api/tasks/bulk/delete` - Bulk delete tasks
- `GET /api/auth/me` - Get current user

### Public Endpoints

These endpoints do not require authentication:

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /health` - Health check

---

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8000/api
```

For production:
```
https://your-domain.com/api
```

---

## Status Codes

The API uses standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| `200 OK` | Request succeeded |
| `201 Created` | Resource created successfully |
| `204 No Content` | Request succeeded, no response body |
| `400 Bad Request` | Invalid request parameters |
| `404 Not Found` | Resource not found |
| `422 Unprocessable Entity` | Validation error in request data |
| `500 Internal Server Error` | Server error |

---

## Endpoints

### Authentication Endpoints

#### Register User

Create a new user account.

##### Request

```http
POST /api/auth/register
Content-Type: application/json
```

##### Request Body

```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "securepass123"
}
```

##### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | **Yes** | Username (3-50 characters, alphanumeric and underscore only) |
| `email` | string | **Yes** | Valid email address (must be unique) |
| `password` | string | **Yes** | Password (minimum 8 characters) |

##### Response

**Status:** `201 Created`

```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-04-01T10:00:00Z"
}
```

**Status:** `409 Conflict` (username or email already exists)

```json
{
  "detail": "Username already registered"
}
```

**Status:** `422 Unprocessable Entity` (validation error)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

##### Validation Rules

- **Username**:
  - 3-50 characters
  - Alphanumeric characters and underscores only
  - Must be unique
- **Email**:
  - Valid email format
  - Must be unique
- **Password**:
  - Minimum 8 characters
  - Should contain mix of uppercase, lowercase, numbers, and special characters (recommended)

##### Examples

**Basic registration:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**JavaScript (Fetch API):**
```javascript
const response = await fetch('http://localhost:8000/api/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'john',
    email: 'john@example.com',
    password: 'securepass123'
  })
});

const user = await response.json();
console.log('User created:', user);
```

**Python (requests):**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/auth/register',
    json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'securepass123'
    }
)

user = response.json()
print(f"User created: {user}")
```

---

#### Login

Authenticate user and receive JWT access token.

##### Request

```http
POST /api/auth/login
Content-Type: application/json
```

##### Request Body

```json
{
  "username": "john",
  "password": "securepass123"
}
```

##### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | **Yes** | Username or email address |
| `password` | string | **Yes** | User password |

##### Response

**Status:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huIiwiZXhwIjoxNzA5MzE2MDAwfQ.signature",
  "token_type": "bearer",
  "expires_in": 1800
}
```

##### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token |
| `token_type` | string | Token type (always "bearer") |
| `expires_in` | integer | Token expiration time in seconds (1800 = 30 minutes) |

**Status:** `401 Unauthorized` (invalid credentials)

```json
{
  "detail": "Incorrect username or password"
}
```

##### Examples

**Basic login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "securepass123"
  }'
```

**Save token to variable (bash):**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "securepass123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

**JavaScript (Fetch API with token storage):**
```javascript
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'john',
    password: 'securepass123'
  })
});

const data = await response.json();

// Store token in localStorage
localStorage.setItem('access_token', data.access_token);

console.log('Logged in successfully');
```

**Python (requests):**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={
        'username': 'john',
        'password': 'securepass123'
    }
)

data = response.json()
token = data['access_token']

print(f"Access token: {token}")
```

##### Token Expiration

- Tokens expire after 30 minutes by default (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` environment variable)
- After expiration, users must login again to get a new token
- The `expires_in` field indicates remaining validity in seconds

---

#### Get Current User

Get information about the currently authenticated user.

##### Request

```http
GET /api/auth/me
Authorization: Bearer <token>
```

##### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | **Yes** | Bearer token: `Bearer <access_token>` |

##### Response

**Status:** `200 OK`

```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-04-01T10:00:00Z"
}
```

**Status:** `401 Unauthorized` (missing or invalid token)

```json
{
  "detail": "Could not validate credentials"
}
```

##### Examples

**Get current user:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Complete authentication flow (bash):**
```bash
# 1. Login and save token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "securepass123"}' \
  | jq -r '.access_token')

# 2. Use token to get current user
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

**JavaScript (Fetch API):**
```javascript
// Get token from localStorage
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const user = await response.json();
console.log('Current user:', user);
```

**Python (requests):**
```python
import requests

headers = {
    'Authorization': f'Bearer {token}'
}

response = requests.get(
    'http://localhost:8000/api/auth/me',
    headers=headers
)

user = response.json()
print(f"Current user: {user}")
```

---

### Health Check

Check if the API server is running and healthy.

#### Request

```http
GET /health
```

#### Response

**Status:** `200 OK`

```json
{
  "status": "healthy"
}
```

#### Example

```bash
curl http://localhost:8000/health
```

---

### Task Endpoints

All task endpoints require authentication. Include the JWT token in the Authorization header.

---

#### Get All Tasks

Retrieve all tasks for the authenticated user with optional filtering and pagination.

##### Request

```http
GET /api/tasks/
Authorization: Bearer <token>
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of records to skip (offset pagination) |
| `limit` | integer | 20 | Maximum number of records to return (max: 100) |
| `page` | integer | null | Page number for page-based pagination (overrides skip) |
| `priority` | string | null | Filter by priority: `low`, `medium`, or `high` |
| `completed` | boolean | null | Filter by completion status |

#### Response

**Status:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "completed": false,
    "priority": "high",
    "tags": "documentation,urgent",
    "due_date": "2024-12-31T23:59:59Z",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "title": "Fix authentication bug",
    "description": "Users cannot login with valid credentials",
    "completed": true,
    "priority": "high",
    "tags": "bug,authentication",
    "due_date": "2024-01-20T18:00:00Z",
    "created_at": "2024-01-14T09:15:00Z",
    "updated_at": "2024-01-16T14:20:00Z"
  }
]
```

#### Examples

**Get first 20 tasks (default):**
```bash
curl "http://localhost:8000/api/tasks/" \
  -H "Authorization: Bearer <your_token>"
```

**Get tasks with pagination:**
```bash
# Offset-based (skip first 20, get next 10)
curl "http://localhost:8000/api/tasks/?skip=20&limit=10"

# Page-based (get page 2 with 20 items per page)
curl "http://localhost:8000/api/tasks/?page=2&limit=20"
```

**Filter by priority:**
```bash
curl "http://localhost:8000/api/tasks/?priority=high"
```

**Filter by completion status:**
```bash
# Get only completed tasks
curl "http://localhost:8000/api/tasks/?completed=true"

# Get only pending tasks
curl "http://localhost:8000/api/tasks/?completed=false"
```

**Combine filters:**
```bash
curl "http://localhost:8000/api/tasks/?priority=high&completed=false&limit=5"
```

---

### Get Single Task

Retrieve a specific task by its ID.

#### Request

```http
GET /api/tasks/{task_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | integer | Unique task identifier |

#### Response

**Status:** `200 OK`

```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "completed": false,
  "priority": "high",
  "tags": "documentation,urgent",
  "due_date": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status:** `404 Not Found` (if task doesn't exist)

```json
{
  "detail": "Task with id 999 not found"
}
```

#### Example

```bash
curl "http://localhost:8000/api/tasks/1"
```

---

### Create Task

Create a new task.

#### Request

```http
POST /api/tasks/
Content-Type: application/json
```

#### Request Body

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "priority": "medium",
  "tags": "shopping,personal",
  "due_date": "2024-01-20T18:00:00Z",
  "completed": false
}
```

#### Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | **Yes** | - | Task title |
| `description` | string | No | `null` | Detailed description |
| `priority` | string | No | `"medium"` | Priority: `low`, `medium`, or `high` |
| `tags` | string | No | `null` | Comma-separated tags |
| `due_date` | datetime | No | `null` | Due date in ISO 8601 format |
| `completed` | boolean | No | `false` | Completion status |

#### Response

**Status:** `201 Created`

```json
{
  "id": 3,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "completed": false,
  "priority": "medium",
  "tags": "shopping,personal",
  "due_date": "2024-01-20T18:00:00Z",
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Status:** `422 Unprocessable Entity` (validation error)

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### Examples

**Minimal task (only title):**
```bash
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task"}'
```

**Full task with all fields:**
```bash
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete quarterly report",
    "description": "Prepare and submit Q1 financial report",
    "priority": "high",
    "tags": "finance,quarterly,report",
    "due_date": "2024-03-31T17:00:00Z",
    "completed": false
  }'
```

---

### Update Task

Update an existing task. All fields are optional - only provided fields will be updated.

#### Request

```http
PUT /api/tasks/{task_id}
Content-Type: application/json
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | integer | Unique task identifier |

#### Request Body

```json
{
  "title": "Buy groceries - Updated",
  "completed": true,
  "priority": "low"
}
```

All fields are optional. Only include fields you want to update.

#### Response

**Status:** `200 OK`

```json
{
  "id": 3,
  "title": "Buy groceries - Updated",
  "description": "Milk, eggs, bread, and vegetables",
  "completed": true,
  "priority": "low",
  "tags": "shopping,personal",
  "due_date": "2024-01-20T18:00:00Z",
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T15:30:00Z"
}
```

**Status:** `404 Not Found`

```json
{
  "detail": "Task with id 999 not found"
}
```

#### Examples

**Mark task as completed:**
```bash
curl -X PUT "http://localhost:8000/api/tasks/3" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Update priority:**
```bash
curl -X PUT "http://localhost:8000/api/tasks/3" \
  -H "Content-Type: application/json" \
  -d '{"priority": "high"}'
```

**Update multiple fields:**
```bash
curl -X PUT "http://localhost:8000/api/tasks/3" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and household items",
    "description": "Milk, eggs, bread, cleaning supplies",
    "tags": "shopping,personal,household",
    "priority": "medium"
  }'
```

---

### Delete Task

Delete a specific task.

#### Request

```http
DELETE /api/tasks/{task_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | integer | Unique task identifier |

#### Response

**Status:** `204 No Content`

No response body.

**Status:** `404 Not Found`

```json
{
  "detail": "Task with id 999 not found"
}
```

#### Example

```bash
curl -X DELETE "http://localhost:8000/api/tasks/3"
```

---

### Search Tasks

Search for tasks using full-text search across title, description, and tags.

#### Request

```http
GET /api/tasks/search
```

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | **Yes** | - | Search query (min 1 character) |
| `limit` | integer | No | 50 | Maximum results (max: 100) |

#### Response

**Status:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Fix urgent bug in authentication",
    "description": "Users cannot login",
    "completed": false,
    "priority": "high",
    "tags": "bug,urgent,authentication",
    "due_date": null,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  },
  {
    "id": 5,
    "title": "Code review",
    "description": "Review urgent pull requests",
    "completed": false,
    "priority": "medium",
    "tags": "review,urgent",
    "due_date": "2024-01-16T17:00:00Z",
    "created_at": "2024-01-15T14:00:00Z",
    "updated_at": "2024-01-15T14:00:00Z"
  }
]
```

**Status:** `422 Unprocessable Entity` (validation error)

```json
{
  "detail": [
    {
      "loc": ["query", "q"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

#### Examples

**Search by keyword:**
```bash
curl "http://localhost:8000/api/tasks/search?q=urgent"
```

**Search with limit:**
```bash
curl "http://localhost:8000/api/tasks/search?q=bug&limit=10"
```

**Search in title, description, or tags:**
```bash
# Searches all three fields
curl "http://localhost:8000/api/tasks/search?q=authentication"
```

---

### Get Statistics

Get comprehensive task statistics including totals, completion status, and priority distribution.

#### Request

```http
GET /api/tasks/stats
```

#### Response

**Status:** `200 OK`

```json
{
  "total": 25,
  "completed": 10,
  "pending": 15,
  "by_priority": {
    "high": 5,
    "medium": 12,
    "low": 8
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total number of tasks |
| `completed` | integer | Number of completed tasks |
| `pending` | integer | Number of pending tasks |
| `by_priority` | object | Task count by priority level |
| `by_priority.high` | integer | Number of high priority tasks |
| `by_priority.medium` | integer | Number of medium priority tasks |
| `by_priority.low` | integer | Number of low priority tasks |

#### Example

```bash
curl "http://localhost:8000/api/tasks/stats"
```

---

### Bulk Delete Tasks

Delete multiple tasks at once.

#### Request

```http
POST /api/tasks/bulk/delete
Content-Type: application/json
```

#### Request Body

```json
{
  "task_ids": [1, 2, 3, 5, 8]
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_ids` | array[integer] | **Yes** | List of task IDs to delete (min: 1 item) |

#### Response

**Status:** `200 OK`

```json
{
  "deleted_count": 5,
  "requested_count": 5
}
```

**Status:** `400 Bad Request` (empty list)

```json
{
  "detail": "task_ids list cannot be empty"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `deleted_count` | integer | Number of tasks actually deleted |
| `requested_count` | integer | Number of task IDs requested for deletion |

> **Note:** `deleted_count` may be less than `requested_count` if some task IDs don't exist.

#### Examples

**Delete multiple tasks:**
```bash
curl -X POST "http://localhost:8000/api/tasks/bulk/delete" \
  -H "Content-Type: application/json" \
  -d '{"task_ids": [1, 2, 3, 4, 5]}'
```

**Delete with partial success:**
```bash
# If task IDs 100 and 200 don't exist
curl -X POST "http://localhost:8000/api/tasks/bulk/delete" \
  -H "Content-Type: application/json" \
  -d '{"task_ids": [1, 100, 2, 200, 3]}'

# Response:
# {
#   "deleted_count": 3,
#   "requested_count": 5
# }
```

---

## Data Models

### User

The User object represents an authenticated user.

```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-04-01T10:00:00Z"
}
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Auto-generated unique identifier |
| `username` | string | Unique username (3-50 characters) |
| `email` | string | Unique email address |
| `is_active` | boolean | User account status |
| `created_at` | datetime | Account creation timestamp (UTC) |

**Note:** The password is never returned in API responses.

### Token

The Token object returned on successful login.

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token |
| `token_type` | string | Token type (always "bearer") |
| `expires_in` | integer | Token expiration time in seconds (1800 = 30 minutes) |

### Task

The main Task object used in all endpoints.

```json
{
  "id": 1,
  "title": "Task title",
  "description": "Optional description",
  "completed": false,
  "priority": "medium",
  "tags": "tag1,tag2,tag3",
  "due_date": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Read-only | Auto-generated unique identifier |
| `title` | string | **Yes** | Task title (1-500 characters) |
| `description` | string \| null | No | Detailed task description |
| `completed` | boolean | No | Completion status (default: `false`) |
| `priority` | string | No | Priority level: `low`, `medium`, `high` (default: `medium`) |
| `tags` | string \| null | No | Comma-separated list of tags |
| `due_date` | datetime \| null | No | Due date in ISO 8601 format |
| `created_at` | datetime | Read-only | Creation timestamp (UTC) |
| `updated_at` | datetime | Read-only | Last update timestamp (UTC) |

#### Priority Levels

- **`low`**: Low priority tasks
- **`medium`**: Medium priority tasks (default)
- **`high`**: High priority tasks

#### Date Format

All datetime fields use ISO 8601 format with timezone:
```
2024-01-20T18:00:00Z
```

---

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages in JSON format.

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error Format

For `422 Unprocessable Entity` responses:

```json
{
  "detail": [
    {
      "loc": ["body", "priority"],
      "msg": "string does not match regex \"^(low|medium|high)$\"",
      "type": "value_error.str.regex"
    }
  ]
}
```

### Common Error Scenarios

#### 1. Missing Required Field

**Request:**
```json
POST /api/tasks/
{
  "description": "Task without title"
}
```

**Response:** `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 2. Invalid Priority Value

**Request:**
```json
POST /api/tasks/
{
  "title": "Task",
  "priority": "urgent"
}
```

**Response:** `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "priority"],
      "msg": "string does not match regex \"^(low|medium|high)$\"",
      "type": "value_error.str.regex"
    }
  ]
}
```

#### 3. Resource Not Found

**Request:**
```http
GET /api/tasks/9999
```

**Response:** `404 Not Found`
```json
{
  "detail": "Task with id 9999 not found"
}
```

#### 4. Empty Bulk Delete List

**Request:**
```json
POST /api/tasks/bulk/delete
{
  "task_ids": []
}
```

**Response:** `400 Bad Request`
```json
{
  "detail": "task_ids list cannot be empty"
}
```

---

## Rate Limiting

**Current Version:** No rate limiting implemented

> **Note:** For production deployments, implement rate limiting to prevent abuse. Recommended limits:
> - 100 requests per minute per IP for read operations
> - 20 requests per minute per IP for write operations

---

## Interactive Documentation

FastAPI provides interactive API documentation:

### Swagger UI
```
http://localhost:8000/docs
```

Features:
- Try out all endpoints
- See request/response schemas
- Test authentication (future)

### ReDoc
```
http://localhost:8000/redoc
```

Features:
- Clean, readable documentation
- Search functionality
- Code samples

---

## Examples

### Complete Workflow with Authentication

Here's a complete workflow demonstrating authentication and task operations:

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123"
  }'

# 2. Login and save token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "securepass123"
  }' | jq -r '.access_token')

echo "Access token: $TOKEN"

# 3. Get current user information
curl "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 4. Create a new task (authenticated)
TASK_ID=$(curl -s -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Deploy to production",
    "description": "Deploy version 2.0",
    "priority": "high",
    "tags": "deployment,production"
  }' | jq -r '.id')

echo "Created task with ID: $TASK_ID"

# 5. Get the task
curl "http://localhost:8000/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"

# 6. Update the task
curl -X PUT "http://localhost:8000/api/tasks/$TASK_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"completed": true}'

# 7. Get statistics
curl "http://localhost:8000/api/tasks/stats" \
  -H "Authorization: Bearer $TOKEN"

# 8. Search for deployment tasks
curl "http://localhost:8000/api/tasks/search?q=deployment" \
  -H "Authorization: Bearer $TOKEN"

# 9. Delete the task
curl -X DELETE "http://localhost:8000/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Authentication-Only Workflow

```bash
# Complete authentication flow
# 1. Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "strongpass456"
  }'

# 2. Login and get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "strongpass456"
  }'

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }

# 3. Use token for all subsequent requests
# Store token and use in Authorization header
```

### Pagination Example

```bash
# Get total count first
TOTAL=$(curl -s "http://localhost:8000/api/tasks/stats" | jq -r '.total')
echo "Total tasks: $TOTAL"

# Get all tasks page by page (20 per page)
PAGE=1
LIMIT=20

while [ $(( (PAGE - 1) * LIMIT )) -lt $TOTAL ]; do
  echo "Fetching page $PAGE..."
  curl "http://localhost:8000/api/tasks/?page=$PAGE&limit=$LIMIT"
  PAGE=$((PAGE + 1))
done
```

### Filtering Example

```bash
# Get all high priority, incomplete tasks
curl "http://localhost:8000/api/tasks/?priority=high&completed=false"

# Get completed tasks, 10 per page
curl "http://localhost:8000/api/tasks/?completed=true&limit=10"

# Get medium priority tasks, page 2
curl "http://localhost:8000/api/tasks/?priority=medium&page=2&limit=20"
```

---

## Changelog

### Version 1.0.0 (Current)

**Added:**
- Complete CRUD operations for tasks
- Priority levels (low, medium, high)
- Tag support
- Due date support
- Full-text search endpoint
- Statistics endpoint
- Bulk delete endpoint
- Filtering by priority and completion status
- Pagination with skip/limit and page parameters

**Future Enhancements:**
- JWT-based authentication
- User accounts and task ownership
- Task categories/projects
- Task assignment to users
- Comments on tasks
- File attachments
- Webhooks for task events
- Rate limiting
- API versioning (v2)

---

## Support

For issues, questions, or feature requests:

- **GitHub Issues**: [Repository Issues](https://github.com/your-repo/issues)
- **API Documentation**: http://localhost:8000/docs
- **Email**: support@example.com

---

**Last Updated:** 2024-01-15
**API Version:** 1.0.0
