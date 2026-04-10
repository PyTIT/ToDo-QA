import uuid
import requests
import pytest

BASE_URL = "http://127.0.0.1:5000"


def register_user(username, password):
    payload = {
        "username": username,
        "password": password
    }

    response = requests.post(f"{BASE_URL}/register", json=payload)
    response_body = response.json()

    return response, response_body


def login_user(username, password):
    payload = {
        "username": username,
        "password": password
    }

    response = requests.post(f"{BASE_URL}/login", json=payload)
    response_body = response.json()

    return response, response_body


def create_task(title, description, priority, headers):
    payload = {
        "title": title,
        "description": description,
        "priority": priority
    }

    response = requests.post(f"{BASE_URL}/tasks", json=payload, headers=headers)
    response_body = response.json()

    return response, response_body

# GET /tasks

from datetime import timedelta
from app import create_app
from flask_jwt_extended import create_access_token


def test_get_tasks_with_valid_token_returns_all_own_tasks():
    unique_suffix_1 = uuid.uuid4().hex[:6]
    username_1 = f"autotest_{unique_suffix_1}"
    password_1 = "Password123"

    register_response_1, register_response_body_1 = register_user(username_1, password_1)
    login_response_1, login_response_body_1 = login_user(username_1, password_1)

    token_1 = login_response_body_1["access_token"]
    headers_1 = {
        "Authorization": f"Bearer {token_1}"
    }

    create_response_1, create_response_body_1 = create_task(
        "task_user_1_first",
        "description_1",
        "high",
        headers_1
    )
    create_response_2, create_response_body_2 = create_task(
        "task_user_1_second",
        "description_2",
        "medium",
        headers_1
    )

    unique_suffix_2 = uuid.uuid4().hex[:6]
    username_2 = f"autotest_{unique_suffix_2}"
    password_2 = "Password123"

    register_response_2, register_response_body_2 = register_user(username_2, password_2)
    login_response_2, login_response_body_2 = login_user(username_2, password_2)

    token_2 = login_response_body_2["access_token"]
    headers_2 = {
        "Authorization": f"Bearer {token_2}"
    }

    create_response_3, create_response_body_3 = create_task(
        "task_user_2",
        "description_3",
        "low",
        headers_2
    )

    response = requests.get(f"{BASE_URL}/tasks", headers=headers_1)
    response_body = response.json()

    assert register_response_1.status_code == 201
    assert register_response_body_1["message"] == "User created successfully"

    assert login_response_1.status_code == 200
    assert "access_token" in login_response_body_1

    assert create_response_1.status_code == 201
    assert create_response_body_1["title"] == "task_user_1_first"

    assert create_response_2.status_code == 201
    assert create_response_body_2["title"] == "task_user_1_second"

    assert register_response_2.status_code == 201
    assert register_response_body_2["message"] == "User created successfully"

    assert login_response_2.status_code == 200
    assert "access_token" in login_response_body_2

    assert create_response_3.status_code == 201
    assert create_response_body_3["title"] == "task_user_2"

    assert response.status_code == 200
    assert isinstance(response_body, list)

    titles = [task["title"] for task in response_body]

    assert "task_user_1_first" in titles
    assert "task_user_1_second" in titles
    assert "task_user_2" not in titles


def test_get_tasks_without_tasks_returns_empty_list():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 200
    assert response_body == []


def test_get_tasks_with_expired_token_returns_401():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    app = create_app()
    with app.app_context():
        expired_token = create_access_token(
            identity="1",
            expires_delta=timedelta(seconds=-1)
        )

    headers = {
        "Authorization": f"Bearer {expired_token}"
    }

    response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 401
    assert "msg" in response_body


def test_get_tasks_with_invalid_token_returns_422():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer f{token}"
    }

    response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 422
    assert "msg" in response_body


def test_get_tasks_without_token_returns_401():
    response = requests.get(f"{BASE_URL}/tasks")
    response_body = response.json()

    assert response.status_code == 401
    assert response_body == {"msg": "Missing Authorization Header"}


def test_get_tasks_with_invalid_authorization_header_format_returns_401():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]

    response = requests.get(
        f"{BASE_URL}/tasks",
        headers={"Authorization": token}
    )
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 401
    assert "msg" in response_body


def test_get_own_task_by_id_returns_200():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response, create_response_body = create_task(
        "task_for_get_by_id",
        "description",
        "high",
        headers
    )
    task_id = create_response_body["id"]

    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response.status_code == 201
    assert create_response_body["title"] == "task_for_get_by_id"

    assert response.status_code == 200
    assert response_body["id"] == task_id
    assert response_body["title"] == "task_for_get_by_id"
    assert response_body["description"] == "description"
    assert response_body["priority"] == "high"


def test_get_other_user_task_by_id_returns_403():
    unique_suffix_1 = uuid.uuid4().hex[:6]
    username_1 = f"autotest_{unique_suffix_1}"
    password_1 = "Password123"

    register_response_1, register_response_body_1 = register_user(username_1, password_1)
    login_response_1, login_response_body_1 = login_user(username_1, password_1)

    token_1 = login_response_body_1["access_token"]
    headers_1 = {
        "Authorization": f"Bearer {token_1}"
    }

    create_response, create_response_body = create_task(
        "task_user_1",
        "description",
        "high",
        headers_1
    )
    task_id = create_response_body["id"]

    unique_suffix_2 = uuid.uuid4().hex[:6]
    username_2 = f"autotest_{unique_suffix_2}"
    password_2 = "Password123"

    register_response_2, register_response_body_2 = register_user(username_2, password_2)
    login_response_2, login_response_body_2 = login_user(username_2, password_2)

    token_2 = login_response_body_2["access_token"]
    headers_2 = {
        "Authorization": f"Bearer {token_2}"
    }

    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers_2)
    response_body = response.json()

    assert register_response_1.status_code == 201
    assert register_response_body_1["message"] == "User created successfully"

    assert login_response_1.status_code == 200
    assert "access_token" in login_response_body_1

    assert create_response.status_code == 201
    assert create_response_body["title"] == "task_user_1"

    assert register_response_2.status_code == 201
    assert register_response_body_2["message"] == "User created successfully"

    assert login_response_2.status_code == 200
    assert "access_token" in login_response_body_2

    assert response.status_code == 403
    assert response_body == {"message": "Forbidden"}


def test_get_non_existent_task_by_id_returns_404():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{BASE_URL}/tasks/999999999", headers=headers)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 404
    assert response_body == {"message": "Task not found"}


def test_get_own_tasks_by_valid_status_returns_200():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response_1, create_response_body_1 = create_task(
        "task_new_status",
        "description_1",
        "high",
        headers
    )
    create_response_2, create_response_body_2 = create_task(
        "task_done_status",
        "description_2",
        "medium",
        headers
    )

    task_id = create_response_body_2["id"]

    patch_response = requests.patch(
        f"{BASE_URL}/tasks/{task_id}/status",
        headers=headers,
        json={"status": "done"}
    )
    patch_response_body = patch_response.json()

    response = requests.get(f"{BASE_URL}/tasks?status=done", headers=headers)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response_1.status_code == 201
    assert create_response_body_1["title"] == "task_new_status"

    assert create_response_2.status_code == 201
    assert create_response_body_2["title"] == "task_done_status"

    assert patch_response.status_code == 200
    assert patch_response_body["status"] == "done"

    assert response.status_code == 200
    assert isinstance(response_body, list)
    assert len(response_body) == 1
    assert response_body[0]["id"] == task_id
    assert response_body[0]["title"] == "task_done_status"
    assert response_body[0]["status"] == "done"

def test_get_own_tasks_by_invalid_status_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response, create_response_body = create_task(
        "task_new_status",
        "description_1",
        "high",
        headers
    )

    response = requests.get(f"{BASE_URL}/tasks?status=invalidone", headers=headers)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response.status_code == 201
    assert create_response_body["title"] == "task_new_status"

    assert response.status_code == 400
    assert response_body == {"message": "Invalid status"}