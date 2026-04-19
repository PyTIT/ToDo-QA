import uuid
from datetime import datetime, timedelta

import requests
from playwright.sync_api import Page, expect
from flask_jwt_extended import create_access_token
from app import create_app

BASE_URL = "http://127.0.0.1:5000"

def setup_user_task_and_open_edit_modal(
    page: Page,
    *,
    title: str | None = None,
    description: str = "Task description",
    priority: str = "medium",
    deadline: str | None = None,
):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)

    task_title = title or f"Task {uuid.uuid4().hex[:6]}"
    task = create_task_via_api(
        token=token,
        title=task_title,
        description=description,
        priority=priority,
        deadline=deadline,
    )

    login_via_ui(page, username, password)
    open_edit_modal_for_task(page, task_title)

    return {
        "username": username,
        "password": password,
        "token": token,
        "task": task,
        "title": task_title,
        "description": description,
        "priority": priority,
    }


def get_task_card(page: Page, title: str):
    return page.locator("#tasksList .task-card", has_text=title).first


def set_edit_priority(page: Page, value: str):
    page.locator("#editTaskPriority").evaluate(
        """(el, priorityValue) => {
            el.value = priorityValue;
            el.dispatchEvent(new Event("change", { bubbles: true }));
        }""",
        value,
    )
    

def create_expired_token():
    app = create_app()
    with app.app_context():
        return create_access_token(identity="1", expires_delta=timedelta(seconds=-1))

def setup_user_and_task_for_delete(page: Page, *, title: str | None = None):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)

    task_title = title or f"Task {uuid.uuid4().hex[:6]}"
    create_task_via_api(
        token=token,
        title=task_title,
        description="Task for delete modal tests",
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

def force_edit_deadline(page: Page, target_dt: datetime):
    display_date = target_dt.strftime("%d.%m.%Y")
    canonical_date = target_dt.strftime("%Y-%m-%d")
    hour_value = target_dt.strftime("%H")
    minute_value = target_dt.strftime("%M")

    page.locator("#editTaskDeadlineDate").fill(display_date)
    page.locator("#editTaskDescription").click()

    page.evaluate(
        """({ displayDate, canonicalDate, hourValue, minuteValue }) => {
            const dateInput = document.querySelector("#editTaskDeadlineDate");
            const nativeDateInput = document.querySelector("#editTaskDeadlineNative");
            const hourInput = document.querySelector("#editTaskDeadlineHour");
            const minuteInput = document.querySelector("#editTaskDeadlineMinute");

            dateInput.value = displayDate;
            dateInput.dataset.canonicalDate = canonicalDate;
            nativeDateInput.value = canonicalDate;

            hourInput.disabled = false;
            minuteInput.disabled = false;
            hourInput.value = hourValue;
            minuteInput.value = minuteValue;
        }""",
        {
            "displayDate": display_date,
            "canonicalDate": canonical_date,
            "hourValue": hour_value,
            "minuteValue": minute_value,
        },
    )


def generate_unique_user():
    suffix = uuid.uuid4().hex[:6]
    return f"uiuser_{suffix}", "Password123"


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
    description: str = "Task description",
    priority: str = "medium",
    deadline: str | None = None,
):
    payload = {
        "title": title,
        "description": description,
        "priority": priority,
        "deadline": deadline,
    }
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
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


def open_edit_modal_for_task(page: Page, task_title: str):
    task_card = page.locator("#tasksList .task-card", has_text=task_title).first
    expect(task_card).to_be_visible()
    task_card.locator('[data-action="edit"]').click()
    expect(page.locator("#editModal")).to_be_visible()
    

def test_successful_task_deletion(page: Page):
    data = setup_user_and_task_for_delete(page)

    data["task_card"].locator('[data-action="delete"]').click()

    expect(page.locator("#deleteModal")).to_be_visible()

    page.locator("#confirmDeleteBtn").click()

    expect(page.locator("#deleteModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Задача удалена.")

    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    expect(page.locator("#tasksList")).not_to_contain_text(data["title"])

    
def test_delete_modal_closes_with_escape(page: Page):
    data = setup_user_and_task_for_delete(page)
    data["task_card"].locator('[data-action="delete"]').click()

    expect(page.locator("#deleteModal")).to_be_visible()

    page.keyboard.press("Escape")

    expect(page.locator("#deleteModal")).to_be_hidden()
    expect(page.locator("#tasksList")).to_contain_text(data["title"])
    
def test_delete_modal_closes_with_x_button(page: Page):
    data = setup_user_and_task_for_delete(page)
    data["task_card"].locator('[data-action="delete"]').click()

    expect(page.locator("#deleteModal")).to_be_visible()

    page.locator("#closeDeleteModalBtn").click()

    expect(page.locator("#deleteModal")).to_be_hidden()
    expect(page.locator("#tasksList")).to_contain_text(data["title"])
    
def test_delete_modal_closes_with_backdrop_click(page: Page):
    data = setup_user_and_task_for_delete(page)
    data["task_card"].locator('[data-action="delete"]').click()

    expect(page.locator("#deleteModal")).to_be_visible()

    page.locator('#deleteModal [data-close-delete-modal="true"]').click(position={"x": 5, "y": 5})

    expect(page.locator("#deleteModal")).to_be_hidden()
    expect(page.locator("#tasksList")).to_contain_text(data["title"])
    
def test_delete_modal_closes_with_cancel_button(page: Page):
    data = setup_user_and_task_for_delete(page)
    data["task_card"].locator('[data-action="delete"]').click()

    expect(page.locator("#deleteModal")).to_be_visible()

    page.locator("#cancelDeleteBtn").click()

    expect(page.locator("#deleteModal")).to_be_hidden()
    expect(page.locator("#tasksList")).to_contain_text(data["title"])
    
def test_delete_task_with_expired_token_logs_out_user_and_keeps_task(page: Page):
    data = setup_user_and_task_for_delete(page)
    expired_token = create_expired_token()

    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )

    data["task_card"].locator('[data-action="delete"]').click()
    expect(page.locator("#deleteModal")).to_be_visible()

    page.locator("#confirmDeleteBtn").click()

    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Сессия истекла. Войдите снова.")

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    expect(page.locator("#deleteModal")).to_be_hidden()

    login_via_ui(page, data["username"], data["password"])
    expect(page.locator("#tasksList")).to_contain_text(data["title"])
    
def test_delete_modal_shows_exact_task_title(page: Page):
    title = f"Delete me {uuid.uuid4().hex[:6]}"
    data = setup_user_and_task_for_delete(page, title=title)

    data["task_card"].locator('[data-action="delete"]').click()

    expect(page.locator("#deleteModal")).to_be_visible()
    expect(page.locator("#deleteModalTaskText")).to_have_text(f"Задача: {title}")