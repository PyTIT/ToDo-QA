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

def test_get_only_my_tasks():
    # ---------- 1. Создаём первого пользователя ----------
    # Делаем уникальный суффикс, чтобы username не повторялся между запусками тестов
    unique_suffix_1 = uuid.uuid4().hex[:6]
    username_1 = f"autotest_{unique_suffix_1}"
    password_1 = "Password123"

    # Регистрируем первого пользователя
    register_response_1, register_response_body_1 = register_user(username_1, password_1)

    # Логинимся под первым пользователем
    login_response_1, login_response_body_1 = login_user(username_1, password_1)

    # Достаём access token первого пользователя
    token_1 = login_response_body_1["access_token"]

    # Готовим headers для авторизованных запросов от имени первого пользователя
    headers_1 = {
        "Authorization": f"Bearer {token_1}"
    }

    # ---------- 2. Создаём задачу первого пользователя ----------
    payload_1 = {
        "title": "task_user_1",
        "description": "description_1",
        "priority": "high"
    }

    # Отправляем POST /tasks с токеном первого пользователя
    create_response_1 = requests.post(f"{BASE_URL}/tasks",headers=headers_1,json=payload_1)
    create_response_body_1 = create_response_1.json()

    # ---------- 3. Создаём второго пользователя ----------
    # Он нужен именно для проверки,
    # что чужие задачи НЕ попадут в ответ первому пользователю
    unique_suffix_2 = uuid.uuid4().hex[:6]
    username_2 = f"autotest_{unique_suffix_2}"
    password_2 = "Password123"

    # Регистрируем второго пользователя
    register_response_2, register_response_body_2 = register_user(username_2, password_2)

    # Логинимся под вторым пользователем
    login_response_2, login_response_body_2 = login_user(username_2, password_2)

    # Достаём токен второго пользователя
    token_2 = login_response_body_2["access_token"]

    # Готовим headers уже для второго пользователя
    headers_2 = {
        "Authorization": f"Bearer {token_2}"
    }

    # ---------- 4. Создаём задачу второго пользователя ----------
    payload_2 = {
        "title": "task_user_2",
        "description": "description_2",
        "priority": "low"
    }

    # Отправляем POST /tasks с токеном второго пользователя
    create_response_2 = requests.post(f"{BASE_URL}/tasks",headers=headers_2,json=payload_2)
    create_response_body_2 = create_response_2.json()

    # ---------- 5. Запрашиваем список задач ПЕРВОГО пользователя ----------
    # Важно: запрос идёт с headers_1,
    # значит сервер должен вернуть только задачи user_1
    response = requests.get(f"{BASE_URL}/tasks",headers=headers_1)
    response_body = response.json()

    # ---------- 6. Базовые проверки по первому пользователю ----------
    assert register_response_1.status_code == 201
    assert register_response_body_1["message"] == "User created successfully"

    assert login_response_1.status_code == 200
    assert "access_token" in login_response_body_1

    assert create_response_1.status_code == 201
    assert create_response_body_1["title"] == "task_user_1"

    # ---------- 7. Базовые проверки по второму пользователю ----------
    assert register_response_2.status_code == 201
    assert register_response_body_2["message"] == "User created successfully"

    assert login_response_2.status_code == 200
    assert "access_token" in login_response_body_2

    assert create_response_2.status_code == 201
    assert create_response_body_2["title"] == "task_user_2"

    # ---------- 8. Проверяем сам GET /tasks ----------
    # Сервер должен вернуть список задач
    assert response.status_code == 200
    assert isinstance(response_body, list)

    # Достаём только titles из всех задач в ответе
    # Например:
    # [{"title": "task_user_1"}, {"title": "task_user_3"}]
    # превратится в:
    # ["task_user_1", "task_user_3"]
    titles = [task["title"] for task in response_body]

    # Проверяем, что задача первого пользователя есть в ответе
    assert "task_user_1" in titles

    # Проверяем, что задача второго пользователя НЕ попала в ответ
    assert "task_user_2" not in titles
