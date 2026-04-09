import uuid
import requests
import pytest
from datetime import datetime, timedelta, timezone

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

def test_patch_task_title_returns_200():
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
    
    new_title = {"title": "new_title"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_title)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body["title"] == "new_title"
    
def test_patch_task_title_only_from_spaces_returns_400():
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
    
    new_title = {"title": "   "}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_title)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Title is required"}
    
def test_patch_task_title_is_empty_returns_400():
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
    
    new_title = {"title": ""}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_title)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Title is required"}
    
def test_patch_task_title_is_too_long_returns_400():
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
    
    new_title = {"title": 81 * "x"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_title)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Title must be from 1 to 80 characters"}
    
def test_patch_task_title_is_max_lenght_and_1_less_then_max_returns_200():
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
    
    new_title = {"title": 80 * "x"}
    new_title_2 = {"title": 79 * "x"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_title)
    response_patch_body = response_patch.json()
    
    response_patch_2 = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_title_2)
    response_patch_body_2 = response_patch_2.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body ["title"] == 80 * "x"
    assert response_patch_body_2 ["title"] == 79 * "x"
    
def test_request_task_without_title_not_change_th_title_returns_200():
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
    
    new_payload = {
        "description": "new_description",
        "priority": "low"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_payload)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body["title"] == "test_task"
    assert response_patch_body["description"] == "new_description"
    assert response_patch_body["priority"] == "low"
    
def test_change_task_description_returns_200():
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
    
    new_descriprion = {"description": "new_emae"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_descriprion)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body["description"] == "new_emae"

def test_patch_task_with_empty_description_returns_200():
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
    
    new_descriprion = {"description": ""}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_descriprion)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body["description"] == ""
    
def test_patch_task_with_description_is_too_long_returns_400():
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
    
    new_descriprion = {"description": 501 * "x"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_descriprion)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Description must be up to 500 characters"}
    
def test_patch_task_with_description_max_lenght_and_1_less_then_max_returns_200():
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
    
    new_descriprion = {"description": 500 * "x"}
    new_descriprion_2 = {"description": 499 * "x"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_descriprion)
    response_patch_body = response_patch.json()
    
    response_patch_2 = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_descriprion_2)
    response_patch_body_2 = response_patch_2.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body["description"] == 500 * "x"
    
    assert response_patch_2.status_code == 200
    assert response_patch_body_2["description"] == 499 * "x"
    
def test_change_priority_returns_200():
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
    
    new_priority = {"priority": "medium"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_priority)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body["priority"] == "medium"
    
def test_change_priority_to_invalid_returns_400():
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
    
    new_priority = {"priority": "invalid_medium"}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_priority)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Priority must be low, medium or high"}
    
def test_change_priority_is_empty_returns_400():
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
    
    new_priority = {"priority": ""}
    
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    response_body = response.json()
    task_id = response_body["id"] 
    
    response_patch = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=new_priority)
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Priority must be low, medium or high"}

def test_patch_task_deadline_with_valid_value_more_than_30_minutes_returns_200():
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

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()

    assert create_response.status_code == 201
    task_id = create_response_body["id"]

    valid_deadline = (datetime.now() + timedelta(minutes=40)).replace(microsecond=0).isoformat()
    patch_payload = {
        "deadline": valid_deadline
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body["id"] == task_id
    assert response_patch_body["deadline"] == f"{valid_deadline}Z"


def test_patch_task_with_id_status_and_created_at_does_not_change_them():
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

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()

    assert create_response.status_code == 201
    task_id = create_response_body["id"]

    patch_payload = {
        "id": 999999,
        "status": "done",
        "created_at": "2020-01-01T00:00:00Z"
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 200
    assert response_patch_body["id"] == create_response_body["id"]
    assert response_patch_body["status"] == create_response_body["status"]
    assert response_patch_body["created_at"] == create_response_body["created_at"]
    assert response_patch_body["title"] == create_response_body["title"]
    assert response_patch_body["description"] == create_response_body["description"]
    assert response_patch_body["priority"] == create_response_body["priority"]


def test_patch_task_without_token_returns_401():
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

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()

    assert create_response.status_code == 201
    task_id = create_response_body["id"]

    patch_payload = {
        "title": "new_title"
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 401
    assert response_patch_body == {"msg": "Missing Authorization Header"}


def test_patch_task_with_invalid_token_returns_422():
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
    valid_headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = requests.post(f"{BASE_URL}/tasks", headers=valid_headers, json=payload)
    create_response_body = create_response.json()

    assert create_response.status_code == 201
    task_id = create_response_body["id"]

    patch_payload = {
        "title": "new_title"
    }

    invalid_headers = {
        "Authorization": f"Bearer f{token}"
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=invalid_headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 422
    assert "msg" in response_patch_body


def test_patch_task_with_invalid_authorization_header_format_returns_401():
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
    valid_headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = requests.post(f"{BASE_URL}/tasks", headers=valid_headers, json=payload)
    create_response_body = create_response.json()

    assert create_response.status_code == 201
    task_id = create_response_body["id"]

    patch_payload = {
        "title": "new_title"
    }

    invalid_headers = {
        "Authorization": token
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=invalid_headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 401
    assert "msg" in response_patch_body

def test_patch_task_with_past_deadline_returns_400():
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

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    past_deadline = (
        datetime.now(timezone.utc) - timedelta(minutes=10)
    ).isoformat().replace("+00:00", "Z")

    patch_payload = {
        "deadline": past_deadline
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response.status_code == 201
    assert response_patch.status_code == 400
    assert response_patch_body == {
        "message": "Deadline must be at least 30 minutes later than current time"
    }


def test_patch_task_with_deadline_less_than_30_minutes_returns_400():
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

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    deadline_less_than_30_minutes = (
        datetime.now(timezone.utc) + timedelta(minutes=20)
    ).isoformat().replace("+00:00", "Z")

    patch_payload = {
        "deadline": deadline_less_than_30_minutes
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response.status_code == 201
    assert response_patch.status_code == 400
    assert response_patch_body == {
        "message": "Deadline must be at least 30 minutes later than current time"
    }


def test_patch_task_with_null_deadline_removes_deadline():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    initial_deadline = (
        datetime.now(timezone.utc) + timedelta(minutes=40)
    ).isoformat().replace("+00:00", "Z")

    payload = {
        "title": "test_task",
        "description": "description",
        "priority": "high",
        "deadline": initial_deadline
    }

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    patch_payload = {
        "deadline": None
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response.status_code == 201
    assert create_response_body["deadline"] is not None

    assert response_patch.status_code == 200
    assert response_patch_body["id"] == task_id
    assert response_patch_body["deadline"] is None


def test_patch_task_with_invalid_deadline_format_returns_400():
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

    create_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)
    create_response_body = create_response.json()
    task_id = create_response_body["id"]

    patch_payload = {
        "deadline": "31-12-2026 12:00"
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response.status_code == 201
    assert response_patch.status_code == 400
    assert response_patch_body == {"message": "Deadline must be a valid ISO datetime"}
    
def test_patch_other_user_task_returns_403():
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

    patch_payload = {
        "title": "new_title"
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=headers_2,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response_1.status_code == 201
    assert register_response_body_1["message"] == "User created successfully"

    assert login_response_1.status_code == 200
    assert "access_token" in login_response_body_1

    assert create_response.status_code == 201
    assert create_response_body["title"] == "test_task"

    assert register_response_2.status_code == 201
    assert register_response_body_2["message"] == "User created successfully"

    assert login_response_2.status_code == 200
    assert "access_token" in login_response_body_2

    assert response_patch.status_code == 403
    assert response_patch_body == {"message": "Forbidden"}


def test_patch_non_existent_task_returns_404():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    token = login_response_body["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    patch_payload = {
        "title": "new_title"
    }

    response_patch = requests.patch(
        f"{BASE_URL}/tasks/999999999",
        headers=headers,
        json=patch_payload
    )
    response_patch_body = response_patch.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert response_patch.status_code == 404
    assert response_patch_body == {"message": "Task not found"}