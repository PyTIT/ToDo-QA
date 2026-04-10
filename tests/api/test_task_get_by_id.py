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

def test_get_tasks_with_existing_search_keyword_returns_matching_tasks():
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
        "pytest smoke task",
        "description_1",
        "high",
        headers_1
    )
    create_response_2, create_response_body_2 = create_task(
        "regular task",
        "contains keyword pytest in description",
        "medium",
        headers_1
    )
    create_response_3, create_response_body_3 = create_task(
        "another task",
        "description without keyword",
        "low",
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

    create_response_4, create_response_body_4 = create_task(
        "pytest foreign task",
        "foreign description",
        "high",
        headers_2
    )

    response = requests.get(f"{BASE_URL}/tasks?search=pytest", headers=headers_1)
    response_body = response.json()

    assert register_response_1.status_code == 201
    assert register_response_body_1["message"] == "User created successfully"

    assert login_response_1.status_code == 200
    assert "access_token" in login_response_body_1

    assert create_response_1.status_code == 201
    assert create_response_2.status_code == 201
    assert create_response_3.status_code == 201

    assert register_response_2.status_code == 201
    assert register_response_body_2["message"] == "User created successfully"

    assert login_response_2.status_code == 200
    assert "access_token" in login_response_body_2

    assert create_response_4.status_code == 201

    assert response.status_code == 200
    assert isinstance(response_body, list)

    titles = [task["title"] for task in response_body]

    assert "pytest smoke task" in titles
    assert "regular task" in titles
    assert "another task" not in titles
    assert "pytest foreign task" not in titles


def test_get_tasks_with_non_existent_search_keyword_returns_empty_list():
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
        "task_one",
        "description_one",
        "high",
        headers
    )
    create_response_2, create_response_body_2 = create_task(
        "task_two",
        "description_two",
        "medium",
        headers
    )

    response = requests.get(f"{BASE_URL}/tasks?search=nonexistentkeyword123", headers=headers)
    response_body = response.json()

    assert register_response.status_code == 201
    assert register_response_body["message"] == "User created successfully"

    assert login_response.status_code == 200
    assert "access_token" in login_response_body

    assert create_response_1.status_code == 201
    assert create_response_2.status_code == 201

    assert response.status_code == 200
    assert response_body == []