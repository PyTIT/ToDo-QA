import re
import uuid
from datetime import timedelta

import requests
from flask_jwt_extended import create_access_token
from playwright.sync_api import Page, expect

from app import create_app

BASE_URL = "http://127.0.0.1:5000"


def generate_unique_user():
    suffix = uuid.uuid4().hex[:6]
    username = f"uiuser_{suffix}"
    password = "Password123"
    return username, password


def register_user_via_api(username: str, password: str):
    response = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 201


def login_user_via_api(username: str, password: str) -> str:
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def create_task_via_api(
    token: str,
    title: str,
    description: str = "Task for status change",
    priority: str = "medium",
    deadline: str | None = None,
):
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "title": title,
            "description": description,
            "priority": priority,
            "deadline": deadline,
        },
    )
    assert response.status_code == 201
    return response.json()


def open_login_form(page: Page):
    page.goto(BASE_URL)
    expect(page.locator("#loginForm")).to_be_visible()
    expect(page.locator("#registerForm")).to_be_hidden()


def login_via_ui(page: Page, username: str, password: str):
    open_login_form(page)

    page.locator("#loginUsername").fill(username)
    page.locator("#loginPassword").fill(password)
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(username)


def create_expired_token():
    app = create_app()
    with app.app_context():
        return create_access_token(identity="1", expires_delta=timedelta(seconds=-1))


def setup_user_and_task_for_status(page: Page, *, title: str | None = None):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)

    task_title = title or f"Task {uuid.uuid4().hex[:6]}"
    create_task_via_api(
        token=token,
        title=task_title,
        description="Task for status change",
        priority="medium",
    )

    login_via_ui(page, username, password)

    task_card = page.locator("#tasksList .task-card", has_text=task_title).first
    expect(task_card).to_be_visible()

    return {
        "username": username,
        "password": password,
        "token": token,
        "title": task_title,
        "task_card": task_card,
    }
    
def test_change_task_status_to_another(page: Page):
    data = setup_user_and_task_for_status(page)
    task_card = data["task_card"]

    task_card.locator('[data-action="status"][data-status="in_progress"]').click()

    expect(page.locator("#messageBox")).to_have_text("Статус обновлён.")
    expect(task_card.locator(".badge-status")).to_have_text("В работе")
    expect(task_card.locator('[data-action="status"][data-status="in_progress"]')).to_have_class(re.compile(r".*is-current.*"))
    
def test_change_task_status_to_the_same(page: Page):
    data = setup_user_and_task_for_status(page)
    task_card = data["task_card"]

    task_card.locator('[data-action="status"][data-status="new"]').click()

    expect(page.locator("#messageBox")).to_have_text("Статус обновлён.")
    expect(task_card.locator(".badge-status")).to_have_text("Новая")
    expect(task_card.locator('[data-action="status"][data-status="new"]')).to_have_class(re.compile(r".*is-current.*"))
    
def test_change_task_status_with_expired_token(page: Page):
    data = setup_user_and_task_for_status(page)
    task_card = data["task_card"]
    expired_token = create_expired_token()

    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )

    task_card.locator('[data-action="status"][data-status="done"]').click()

    expect(page.locator("#messageBox")).to_have_text("Не удалось изменить статус.")
    expect(task_card.locator(".badge-status")).to_have_text("Новая")
    expect(task_card.locator('[data-action="status"][data-status="new"]')).to_have_class(re.compile(r".*is-current.*"))