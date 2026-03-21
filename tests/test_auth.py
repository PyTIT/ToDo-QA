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