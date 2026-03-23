import uuid
import requests

BASE_URL = "http://127.0.0.1:5000"


def register_user(username, password):
    payload = {
        "username": username,
        "password": password
    }

    response = requests.post(f"{BASE_URL}/register", json=payload)
    response_body = response.json()

    return response, response_body

def login_user(username,password):
    payload = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/login", json=payload)
    response_body = response.json()

    return response, response_body

def create_task(title,description,priority, headers):
    payload = {
        "title": title,
        "description": description,
        "priority": priority
    }
    
    response = requests.post(f"{BASE_URL}/tasks", json=payload, headers=headers)
    response_body = response.json()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return response, response_body


def test_successful_login():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

def test_login_with_invalid_password():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password = f"invalid_{password}")

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 401
    assert login_response_body["message"] == "Invalid username or password"

def test_successful_registration():
    unique_suffix = uuid.uuid4().hex[:7]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "Password123")

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"

def test_successful_registration_with_min_username_length():
    unique_suffix = uuid.uuid4().hex[:2]
    username = f"a{unique_suffix}"

    response, response_body = register_user(username, "Password123")

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"


def test_successful_registration_with_max_username_length():
    unique_suffix = uuid.uuid4().hex[:21]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "Password123")

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"
    

def test_successful_registration_with_min_password_length():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "Passwo12")

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"


def test_successful_registration_with_max_password_length():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "Passwordtest12345678901234567890")

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"


def test_registration_with_invalid_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "1")

    assert response.status_code == 400
    assert response_body["message"] == "Password must be from 8 to 32 characters"
    

def test_registration_with_existing_username_returns_409():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    first_response, first_response_body = register_user(username, password)
    second_response, second_response_body = register_user(username, password)

    assert first_response.status_code == 201
    assert first_response_body["message"] == "User created successfully"

    assert second_response.status_code == 409
    assert second_response_body["message"] == "Username already exists"
    

def test_get_tasks_without_token_returns_401():
    response = requests.get(f"{BASE_URL}/tasks")
    response_body = response.json()

    assert response.status_code == 401
    assert "msg" in response_body
    

def test_get_tasks_with_token_returns_200():
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
    assert isinstance(response_body, list)
    
def test_create_task():
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, password)
    
    payload = {
        "title": "Test",
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

def test_create_task_witout_title_returns_400():
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
