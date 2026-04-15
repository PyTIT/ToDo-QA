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


def test_edit_task_title_with_another_valid_value(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)

    original_title = f"Task {uuid.uuid4().hex[:6]}"
    new_title = f"Updated {uuid.uuid4().hex[:6]}"

    create_task_via_api(
        token=token,
        title=original_title,
        description="Smoke edit task",
        priority="medium",
    )

    login_via_ui(page, username, password)
    open_edit_modal_for_task(page, original_title)

    page.locator("#editTaskTitle").fill(new_title)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_title)
    expect(page.locator("#tasksList")).not_to_contain_text(original_title)


def test_open_edit_modal_contains_existing_task_data(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)

    deadline_value = (datetime.now() + timedelta(days=1)).replace(second=0, microsecond=0)
    deadline_iso = deadline_value.isoformat()

    title = f"Task {uuid.uuid4().hex[:6]}"
    description = "Existing task description"

    create_task_via_api(
        token=token,
        title=title,
        description=description,
        priority="high",
        deadline=deadline_iso,
    )

    login_via_ui(page, username, password)
    open_edit_modal_for_task(page, title)

    expect(page.locator("#editTaskTitle")).to_have_value(title)
    expect(page.locator("#editTaskDescription")).to_have_value(description)
    expect(page.locator("#editTaskPriority")).to_have_value("high")
    expect(page.locator("#editTaskDeadlineDate")).not_to_have_value("")
    expect(page.locator("#editTaskTitle")).to_be_focused()


def test_edit_task_title_with_only_spaces_shows_inline_error(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)

    title = f"Task {uuid.uuid4().hex[:6]}"
    description = "Task for invalid title edit"

    create_task_via_api(
        token=token,
        title=title,
        description=description,
        priority="medium",
    )

    login_via_ui(page, username, password)
    open_edit_modal_for_task(page, title)

    page.locator("#editTaskTitle").fill("   ")
    page.locator("#editTaskDescription").click()

    expect(page.locator("#editTaskTitleError")).to_be_visible()
    expect(page.locator("#editTaskTitleError")).to_have_text("Название задачи обязательно.")
    expect(page.locator("#editTaskTitle")).to_have_class("is-invalid")

    expect(page.locator("#editModal")).to_be_visible()
    
def test_edit_task_title_is_empty_shows_inline_error(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)

    title = f"Task {uuid.uuid4().hex[:6]}"
    description = "Task for invalid title edit"

    create_task_via_api(
        token=token,
        title=title,
        description=description,
        priority="medium",
    )

    login_via_ui(page, username, password)
    open_edit_modal_for_task(page, title)

    page.locator("#editTaskTitle").fill("")
    page.locator("#editTaskDescription").click()

    expect(page.locator("#editTaskTitleError")).to_be_visible()
    expect(page.locator("#editTaskTitleError")).to_have_text("Название задачи обязательно.")
    expect(page.locator("#editTaskTitle")).to_have_class("is-invalid")

    expect(page.locator("#editModal")).to_be_visible()
    
def test_edit_task_title_longer_by_1_character_shows_inline_error(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)

    title = f"Task {uuid.uuid4().hex[:6]}"
    description = "Task for invalid title edit"

    create_task_via_api(
        token=token,
        title=title,
        description=description,
        priority="medium",
    )

    login_via_ui(page, username, password)
    open_edit_modal_for_task(page, title)

    page.locator("#editTaskTitle").fill("121121121121121121121121121121121121121121121121121121121121121121121121121121121")
    page.locator("#editTaskDescription").click()

    expect(page.locator("#editTaskTitleError")).to_be_visible()
    expect(page.locator("#editTaskTitleError")).to_have_text("Название должно быть не длиннее 80 символов.")
    expect(page.locator("#editTaskTitle")).to_have_class("is-invalid")

    expect(page.locator("#editModal")).to_be_visible()
    
def test_edit_task_title_one_char_shorter_than_max_length(page: Page):
    data = setup_user_task_and_open_edit_modal(page)
    new_title = "a" * 79

    page.locator("#editTaskTitle").fill(new_title)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_title)

def test_edit_task_with_title_max_length(page: Page):
    data = setup_user_task_and_open_edit_modal(page)
    new_title = "a" * 80

    page.locator("#editTaskTitle").fill(new_title)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_title)

def test_edit_task_description_with_another_valid_value(page: Page):
    data = setup_user_task_and_open_edit_modal(page)
    new_description = "Updated description from Playwright"

    page.locator("#editTaskDescription").fill(new_description)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_description)


def test_edit_task_with_empty_description(page: Page):
    data = setup_user_task_and_open_edit_modal(page, description="Initial description")

    page.locator("#editTaskDescription").fill("")
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    task_card = get_task_card(page, data["title"])
    expect(task_card).to_contain_text("Без описания")


def test_edit_task_description_too_long(page: Page):
    setup_user_task_and_open_edit_modal(page)

    page.locator("#editTaskDescription").fill("a" * 501)
    page.locator("#editTaskTitle").click()

    expect(page.locator("#editTaskDescriptionError")).to_be_visible()
    expect(page.locator("#editTaskDescriptionError")).to_have_text("Описание должно быть не длиннее 500 символов.")
    expect(page.locator("#editTaskDescription")).to_have_class("is-invalid")
    expect(page.locator("#editModal")).to_be_visible()


def test_edit_task_description_with_max_length(page: Page):
    data = setup_user_task_and_open_edit_modal(page)
    new_description = "a" * 500

    page.locator("#editTaskDescription").fill(new_description)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_description)


def test_edit_task_description_one_char_shorter_than_max_length(page: Page):
    data = setup_user_task_and_open_edit_modal(page)
    new_description = "a" * 499

    page.locator("#editTaskDescription").fill(new_description)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_description)


def test_edit_task_priority_with_another_valid_value(page: Page):
    data = setup_user_task_and_open_edit_modal(page, priority="medium")

    set_edit_priority(page, "high")
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    task_card = get_task_card(page, data["title"])
    expect(task_card.locator(".badge-priority")).to_contain_text("Высокий")


def test_edit_task_deadline_less_than_30_minutes_shows_error(page: Page):
    setup_user_task_and_open_edit_modal(page)

    force_edit_deadline(page, datetime.now() + timedelta(minutes=10))
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editTaskDeadlineError")).to_be_visible()
    expect(page.locator("#editTaskDeadlineError")).to_have_text("Дедлайн должен быть минимум на 30 минут позже текущего времени.")
    expect(page.locator("#editModal")).to_be_visible()


def test_edit_task_clear_deadline(page: Page):
    deadline_iso = (datetime.now() + timedelta(days=1)).replace(second=0, microsecond=0).isoformat()
    data = setup_user_task_and_open_edit_modal(page, deadline=deadline_iso)

    page.locator("#clearEditDeadlineBtn").click()
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    task_card = get_task_card(page, data["title"])
    expect(task_card).to_contain_text("Без дедлайна")


def test_edit_task_change_deadline_to_valid_value(page: Page):
    data = setup_user_task_and_open_edit_modal(page)

    force_edit_deadline(page, datetime.now() + timedelta(days=1, hours=1))
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    task_card = get_task_card(page, data["title"])
    expect(task_card).not_to_contain_text("Без дедлайна")


def test_open_edit_modal_for_task_without_deadline(page: Page):
    setup_user_task_and_open_edit_modal(page, deadline=None)

    expect(page.locator("#editTaskDeadlineDate")).to_have_value("")
    expect(page.locator("#editTaskDeadlineHour")).to_have_value("")
    expect(page.locator("#editTaskDeadlineMinute")).to_have_value("")


def test_edit_task_cancel_button_closes_modal(page: Page):
    setup_user_task_and_open_edit_modal(page)

    page.locator("#cancelEditBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()


def test_edit_task_escape_closes_modal(page: Page):
    setup_user_task_and_open_edit_modal(page)

    page.keyboard.press("Escape")

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()


def test_edit_task_close_button_closes_modal(page: Page):
    setup_user_task_and_open_edit_modal(page)

    page.locator("#closeEditModalBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()


def test_edit_task_backdrop_click_closes_modal(page: Page):
    setup_user_task_and_open_edit_modal(page)

    page.locator('#editModal [data-close-modal="true"]').click(position={"x": 5, "y": 5})

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()


def test_edit_task_without_changes_shows_no_changes_message(page: Page):
    setup_user_task_and_open_edit_modal(page)

    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Изменений нет.")
    
def test_edit_task_with_expired_token_shows_error(page: Page):
    data = setup_user_task_and_open_edit_modal(page)
    expired_token = create_expired_token()

    page.locator("#editTaskTitle").fill("Updated with expired token")

    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )

    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Не удалось сохранить изменения.")


def test_task_card_does_not_change_after_unsuccessful_edit(page: Page):
    data = setup_user_task_and_open_edit_modal(page)
    expired_token = create_expired_token()
    original_title = data["title"]
    new_title = "Should not be saved"

    page.locator("#editTaskTitle").fill(new_title)

    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )

    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_have_text("Не удалось сохранить изменения.")
    expect(page.locator("#editModal")).to_be_visible()
    expect(page.locator("#tasksList")).to_contain_text(original_title)
    expect(page.locator("#tasksList")).not_to_contain_text(new_title)