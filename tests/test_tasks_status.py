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

# PATCH /tasks/<id>/status

def test_change_task_status():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    new_status = {"status": "in_progress"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers=headers, json=new_status)
    response_patch_body = response_patch.json()
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 200
    assert response_patch_body["status"] == "in_progress"
    assert response_patch_body["id"] == task_id
    
def test_change_task_status_without_authorization_header_returns_401():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    new_status = {"status": "in_progress"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", json=new_status)
    response_patch_body = response_patch.json()
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 401
    assert response_patch_body == {"msg": "Missing Authorization Header"}
    
def test_change_task_status_to_same_value_returns_200():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    new_status = {"status": "in_progress"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers=headers, json=new_status)
    response_patch_body = response_patch.json()
    
    response_patch_1 = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers=headers, json=new_status)
    response_patch_body_1 = response_patch.json()
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 200
    assert response_patch_body["status"] == "in_progress"
    assert response_patch_body["id"] == task_id

    assert response_patch_1.status_code == 200
    assert response_patch_body_1["status"] == "in_progress"
    assert response_patch_body_1["id"] == task_id

def test_change_task_invalid_status_return_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    new_status = {"status": "invalid_status"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers=headers,json=new_status)
    response_patch_body = response_patch.json()
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Invalid status"}
    
def test_change_task_status_without_status_field_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers=headers, json=payload)
    response_patch_body = response_patch.json()
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Status is required"}

def test_change_other_user_task_returns_403():
    unique_suffix_1 = uuid.uuid4().hex[:6]
    username_1 = f"autotest_{unique_suffix_1}"
    password_1 = "Password123"

    register_response_1, register_response_body_1 = register_user(username_1, password_1)
    login_response_1, login_response_body_1 = login_user(username_1, password_1)

    token_1 = login_response_body_1["access_token"]
    headers_1 = {
        "Authorization": f"Bearer {token_1}"
    }

    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers_1, json=payload)
    create_response_body = create_response.json()
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

    new_status = {
        "status": "in_progress"
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}/status",
        headers=headers_2,
        json=new_status
    )
    response_patch_body = response_patch.json()

    assert register_response_1.status_code == 201
    assert register_response_body_1["message"] == "User created successfully"

    assert login_response_1.status_code == 200
    assert "access_token" in login_response_body_1

    assert create_response.status_code == 201
    assert create_response_body["title"] == "test_task"
    assert create_response_body["status"] == "new"

    assert register_response_2.status_code == 201
    assert register_response_body_2["message"] == "User created successfully"

    assert login_response_2.status_code == 200
    assert "access_token" in login_response_body_2

    assert response_patch.status_code == 403
    assert response_patch_body == {"message": "Forbidden"}
    
def test_change_task_status_with_invalid_format_auth_header_returns422():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high",
        "status": "high"
    }

    new_status = {
        "status": "in_progress"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers={"Authorization": f"Bearer f{token}"}, json=new_status)
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 422

def test_change_non_exist_task_status():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    new_status = {"status": "in_progress"}
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/999999/status", headers=headers, json=new_status)
    response_patch_body = response_patch.json()
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response_patch.status_code == 404
    assert response_patch_body == {"message": "Task not found"}
    
    
def test_change_task_status_with_empty_status_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    new_status = {
        "status": ""
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers=headers, json=new_status)
    response_patch_body = response_patch.json()
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Status is required"}
    
    
def test_change_task_status_with_extra_fields_updates_only_status():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }
    
    payload_with_status = {
        "title": "new_task",
        "description": "new_description",
        "priority": "high",
        "status": "done"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers=headers, json=payload_with_status)
    response_patch_body = response_patch.json()
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 200
    assert response_patch_body["title"] == "test_task"
    assert response_patch_body["description"] == "description"
    
def test_change_task_status_with_invalid_auth_header():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    new_status = {"status": "in_progress"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", headers={"Authorization": f"Bearer f1{token}"}, json=new_status)
    
    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["status"] == "new"
    
    assert response_patch.status_code == 422