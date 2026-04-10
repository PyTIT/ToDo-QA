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

# DELETE /tasks/<id>

def test_delete_task():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    delete_response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)

    response_get = requests.get(f"{BASE_URL}/tasks", headers=headers)
    response_get_body = response_get.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response.status_code == 201
    assert create_response_body["title"] == "Тестовый заголовок"
    assert create_response_body["status"] == "new"
    assert "created_at" in create_response_body

    assert delete_response.status_code == 204

    assert response_get.status_code == 200
    assert isinstance(response_get_body, list)

    task_ids = [task["id"] for task in response_get_body]
    assert task_id not in task_ids

def test_delete_same_task_twice_returns_404():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    delete_response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    delete_response_2 = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert create_response.status_code == 201

    assert delete_response.status_code == 204
    assert delete_response_2.status_code == 404
    assert delete_response_2.json() == {"message": "Task not found"}

def test_delete_non_existent_task_returns_404():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }


    delete_response = requests.delete(f"{BASE_URL}/tasks/999999999", headers=headers)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert delete_response.status_code == 404
    assert delete_response.json() == {"message": "Task not found"}

def test_delete_other_user_task_returns_403():
    unique_suffix_1 = uuid.uuid4().hex[:6]
    username_1 = f"autotest_{unique_suffix_1}"
    password_1 = "Password123"

    register_response_1, register_response_body_1 = register_user(username_1, password_1)
    login_response_1, login_response_body_1 = login_user(username_1, password_1)

    token_1 = login_response_body_1["access_token"]
    headers_1 = {"Authorization": f"Bearer {token_1}"}

    payload_1 = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    create_response_1 = requests.post(f"{BASE_URL}/tasks", headers=headers_1, json=payload_1)
    create_response_body_1 = create_response_1.json()
    task_id = create_response_body_1["id"]

    unique_suffix_2 = uuid.uuid4().hex[:6]
    username_2 = f"autotest_{unique_suffix_2}"
    password_2 = "Password123"

    register_response_2, register_response_body_2 = register_user(username_2, password_2)
    login_response_2, login_response_body_2 = login_user(username_2, password_2)

    token_2 = login_response_body_2["access_token"]
    headers_2 = {"Authorization": f"Bearer {token_2}"}

    response_delete = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers_2)
    response_delete_body = response_delete.json()

    assert register_response_1.status_code == 201
    assert register_response_body_1["message"] == "User created successfully"

    assert login_response_1.status_code == 200
    assert "access_token" in login_response_body_1

    assert create_response_1.status_code == 201
    assert create_response_body_1["title"] == "test_task"

    assert register_response_2.status_code == 201
    assert register_response_body_2["message"] == "User created successfully"

    assert login_response_2.status_code == 200
    assert "access_token" in login_response_body_2

    assert response_delete.status_code == 403
    assert response_delete_body == {"message": "Forbidden"}

def test_delete_task_without_authorization_header_returns_401():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    token = login_response_body["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "high"
    }

    create_response = requests.post(f"{BASE_URL}/tasks",headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    delete_response = requests.delete(f"{BASE_URL}/tasks/{task_id}")

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"
    
    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert delete_response.status_code == 401
    assert delete_response.json() == {"msg": "Missing Authorization Header"}

def test_delete_task_with_invalid_authorization_header_returns_422():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    token = login_response_body["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "high"
    }

    create_response = requests.post(f"{BASE_URL}/tasks",headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    delete_response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers={"Authorization": f"Bearer f{token}"})

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"
    
    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert delete_response.status_code == 422

def test_delete_task_with_invalid_format_authorization_header_returns_401():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    token = login_response_body["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "high"
    }

    create_response = requests.post(f"{BASE_URL}/tasks",headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    delete_response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers={"Authorization": token})

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"
    
    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert delete_response.status_code == 401
