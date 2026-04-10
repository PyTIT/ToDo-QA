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

# POST /register

def test_successful_registration():
    unique_suffix = uuid.uuid4().hex[:7]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "Password123")

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"

def test_registration_with_spaces_in_login_returns_400():
    unique_suffix = uuid.uuid4().hex[:7]
    username = f"aut  otest_{unique_suffix}"

    response, response_body = register_user(username, "Password123")

    assert response.status_code == 400
    assert response_body["message"] == "Username must not contain spaces"

def test_registration_with_spaces_in_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:7]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "Passw  ord123")

    assert response.status_code == 400
    assert response_body["message"] == "Password must not contain spaces"

def test_registration_without_login_returns_400():

    response, response_body = register_user("", "Password123!")

    assert response.status_code == 400
    assert response_body["message"] == "Username is required"

def test_registration_login_only_with_digits_returns_400():

    response, response_body = register_user("123", "Password123!")

    assert response.status_code == 400
    assert response_body["message"] == "Username must not contain only digits"

def test_registration_login_with_сyrillic_returns_400():

    response, response_body = register_user("123csкирил", "Password123!")

    assert response.status_code == 400
    assert response_body["message"] == "Username must not contain Cyrillic characters"

def test_registration_password_with_сyrillic_returns_400():
    unique_suffix = uuid.uuid4().hex[:7]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "Пароль123К!")

    assert response.status_code == 400
    assert response_body["message"] == "Password must not contain Cyrillic characters"

def test_registration_login_only_with_spaces_returns_400():

    response, response_body = register_user("   ", "Password123!")

    assert response.status_code == 400
    assert response_body["message"] == "Username is required"

def test_registration_without_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:7]
    username = f"autotest_{unique_suffix}"
    
    response, response_body = register_user(username, "")

    assert response.status_code == 400
    assert response_body["message"] == "Password is required"

def test_successful_registration_with_min_username_length():
    unique_suffix = uuid.uuid4().hex[:2]
    username = f"v{unique_suffix}"

    response, response_body = register_user(username, "Password123")

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"

def test_successful_registration_with_max_username_length():
    unique_suffix = uuid.uuid4().hex[:21]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "Password123")

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"

@pytest.mark.parametrize("username", ["ab", "a" * 31])
def test_registration_with_invalid_username_length(username):
    response, response_body = register_user(username, "Password123")

    assert response.status_code == 400
    assert response_body["message"] == "Username must be from 3 to 30 characters"

@pytest.mark.parametrize("password", ["Passwo1!", "Passwordtest12345678901234567890"])
def test_successful_registration_with_valid_password_boundaries(password):
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, password)

    assert response.status_code == 201
    assert response_body["message"] == "User created successfully"

def test_registration_without_letters_in_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "12345678")

    assert response.status_code == 400
    assert response_body["message"] == "Password must contain at least one Latin letter"

def test_registration_without_numbers_in_password_returns_400():
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, "abcdefgh")

    assert response.status_code == 400
    assert response_body["message"] == "Password must contain at least one digit"

@pytest.mark.parametrize("password", ["pass1!", "Passwordtest12345678901234567890!!!"])
def test_registration_with_invalid_password_length_returns_400(password):
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"autotest_{unique_suffix}"

    response, response_body = register_user(username, password)

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
