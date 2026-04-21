import uuid
import requests
import pytest
from datetime import datetime, timedelta, timezone
from app import create_app
from flask_jwt_extended import create_access_token


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


def create_task(title, description, priority, headers,deadline):
    payload = {
        "title": title,
        "description": description,
        "priority": priority,
        "deadline": deadline
    }

    response = requests.post(f"{BASE_URL}/tasks", json=payload, headers=headers)
    response_body = response.json()

    return response, response_body

# POST /tasks

def test_create_task():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "high",
        "deadline": "2026-12-12T18:30:00Z"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert "created_at" in response_body 
    assert payload["title"] == response_body["title"]
    assert payload["description"] == response_body["description"]
    assert payload["priority"] == response_body["priority"]

def test_create_task_without_title_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "description": "description",
        "priority": "hard"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 400

def test_create_task_title_only_spaces_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "   ",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 400

def test_create_task_title_empty_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 400
    
def test_create_task_with_title_is_longer_than_allowed_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabc",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 400
    assert response_body == {"message": "Title must be from 1 to 80 characters"}
    
def test_create_task_with_title_is_max_lenght():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "abcdefghijklmnopqrstuvwxyzabdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabc",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert "created_at" in response_body 
    assert payload["title"] == response_body["title"]
    assert payload["description"] == response_body["description"]
    assert payload["priority"] == response_body["priority"]
    
def test_create_task_with_title_max_length_minus_one_returns_201():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "abcdefghijklmnopqrstuvwxyzabdefgijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabc",
        "description": "description",
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    
def test_create_task_with_empty_description():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "",
        "priority": "high",
        "deadline": "2026-12-12T18:30:00Z"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201  
    
def test_create_task_with_description_longer_than_max_length_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    payload = {
        "title": "test_task",
        "description": "a" * 501,
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 400
    assert response_body == {"message": "Description must be up to 500 characters"}


def test_create_task_with_max_description_length_returns_201():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    payload = {
        "title": "test_task",
        "description": "a" * 500,
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 201


def test_create_task_with_description_one_character_shorter_than_max_length_returns_201():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    payload = {
        "title": "test_task",
        "description": "a" * 499,
        "priority": "high"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 201
    
def test_create_task_with_invalid_priority_returns_400():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "invalid",
        "deadline": "2026-12-12T18:30:00Z"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 400
    assert response_body == {"message": "Priority must be low, medium or high"}
    
def test_create_task_without_priority_sets_medium_by_default():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",\
        "priority": None,
        "deadline": "2026-12-12T18:30:00Z"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["priority"] == "medium"
    
def test_create_task_with_deadline_is_the_past():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",\
        "priority": "low",
        "deadline": "2026-04-04T18:30:00Z"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 400
    assert response_body == {"message": "Deadline must be at least 30 minutes later than current time"}

def test_create_task_with_deadline_less_than_30_minutes_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    deadline_less_than_30_minutes = (
        datetime.now(timezone.utc) + timedelta(minutes=20)
    ).isoformat().replace("+00:00", "Z")

    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high",
        "deadline": deadline_less_than_30_minutes
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 400
    assert response_body == {
        "message": "Deadline must be at least 30 minutes later than current time"
    }

def test_create_task_with_deadline_is_null_returns_201():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "low",
        "deadline": None
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["deadline"] == None
    
def test_create_task_without_deadline_returns_201():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "low"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 201
    assert response_body["deadline"] == None
    
def test_create_task_with_deadline_is_invalid_format_returns_400():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "low",
        "deadline": "2027-31-07T18:30:00"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 400
    assert response_body == {"message": "Deadline must be a valid ISO datetime"}
    
def test_create_task_without_auth_header_returns_401():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "high",
        "deadline": "2026-12-12T18:30:00Z"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 401
    assert response_body == {"msg": "Missing Authorization Header"}
    
def test_create_task_with_invalid_format_auth_header_returns_401():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "low",
        "deadline": "2027-12-12T18:30:00"
    }

    token = login_response_body["access_token"]
    
    response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": token}, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 401
    assert response_body == {"msg": "Missing 'Bearer' type in 'Authorization' header. Expected 'Authorization: Bearer <JWT>'"}

def test_create_task_with_unvalid_auth_header_returns_422():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Тестовый заголовок",
        "description": "description",
        "priority": "high",
        "deadline": "2026-12-12T18:30:00Z"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer f{token}"}, json=payload)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
    
    assert response.status_code == 422
    
def test_create_task_with_extra_fields_ignores_them():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high",
        "status": "done",
        "id": 999999,
        "user_id": 999999,
        "created_at": "2020-01-01T00:00:00Z",
        "extra_field": "should_be_ignored"
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 201
    assert response_body["title"] == "test_task"
    assert response_body["description"] == "description"
    assert response_body["priority"] == "high"

    assert response_body["status"] == "new"
    assert response_body["id"] != 999999
    assert response_body["created_at"] != "2020-01-01T00:00:00Z"

    assert "user_id" not in response_body
    assert "extra_field" not in response_body
    
def test_create_task_with_expired_token_returns_401():
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

    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high"
    }

    headers = {
        "Authorization": f"Bearer {expired_token}"
    }

    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response.status_code == 401
    assert "msg" in response_body