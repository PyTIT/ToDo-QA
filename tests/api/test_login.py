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

# POST /login

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

def test_login_with_invalid_username_returns_401():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(f"invalid_{username}", password)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 401
    assert login_response_body["message"] == "Invalid username or password"

def test_login_with_invalid_username_and_password_returns_401():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(f"invalid_{username}", f"invalid_{password}")

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 401
    assert login_response_body["message"] == "Invalid username or password"

def test_login_without_username_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user("", password)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 400
    assert login_response_body["message"] == "Username is required"

def test_login_without_username_and_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user("", "")

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 400
    assert login_response_body["message"] == "Username is required"

def test_login_with_spaces_in_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, "Pass word123")

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 400
    assert login_response_body["message"] == "Password must not contain spaces"

def test_login_with_spaces_in_username_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(f"auto test_{unique_suffix}", password)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 400
    assert login_response_body["message"] == "Username must not contain spaces"

def test_login_with_spaces_after_username_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(f"{username} ", password)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 400
    assert login_response_body["message"] == "Username must not contain spaces"

def test_login_with_spaces_before_username_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(f" {username}", password)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 400
    assert login_response_body["message"] == "Username must not contain spaces"

def test_login_with_spaces_after_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, f"{password} ")

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 400
    assert login_response_body["message"] == "Password must not contain spaces"

def test_login_with_spaces_before_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"

    register_response, register_response_body = register_user(username, password)
    login_response, login_response_body = login_user(username, f" {password}")

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 400
    assert login_response_body["message"] == "Password must not contain spaces"

def test_successful_login_with_non_existent_field():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"
    invalid_field = "invalid_value"

    register_response, register_response_body = register_user(username, password, invalid_field)
    login_response, login_response_body = login_user(username, password, invalid_field)

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

def test_successful_login_with_non_existent_field():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"
    password = "Password123"
    invalid_field = "invalid_value"

    # Регистрация с дополнительным полем
    register_payload = {
        "username": username,
        "password": password,
        "invalid_field": invalid_field
    }
    register_response = requests.post(f"{BASE_URL}/register", json=register_payload)
    register_response_body = register_response.json()

    # Логин с дополнительным полем
    login_payload = {
        "username": username,
        "password": password,
        "invalid_field": invalid_field
    }
    login_response = requests.post(f"{BASE_URL}/login", json=login_payload)
    login_response_body = login_response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body
