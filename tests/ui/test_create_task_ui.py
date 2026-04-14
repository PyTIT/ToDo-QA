import uuid
from datetime import datetime, timedelta
from app import create_app
from flask_jwt_extended import create_access_token

import requests
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5000"


def generate_unique_user():
    suffix = uuid.uuid4().hex[:6]
    username = f"uiuser_{suffix}"
    password = "Password123"
    return username, password


def register_user_via_api(username, password):
    response = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 201


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

def set_task_priority(page: Page, value: str):
    page.locator("#taskPriority").evaluate(
        """(el, priorityValue) => {
            el.value = priorityValue;
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        value,
    )


def fill_valid_deadline(page: Page):
    future_date = datetime.now() + timedelta(days=1)
    ui_date = future_date.strftime("%d.%m.%Y")

    page.locator("#taskDeadlineDate").fill(ui_date)

    # Уводим фокус, чтобы сработала логика deadline picker
    page.locator("#taskDescription").click()

    page.wait_for_function(
        """
        () => {
            const hour = document.querySelector("#taskDeadlineHour");
            const minute = document.querySelector("#taskDeadlineMinute");
            return hour && minute && hour.value !== "" && minute.value !== "";
        }
        """
    )


def test_create_task_with_all_valid_fields_task_appears_form_is_cleared_and_success_message_is_shown(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    title = f"UI task {uuid.uuid4().hex[:6]}"
    description = "Task created by Playwright smoke test"

    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill(description)
    set_task_priority(page, "high")
    fill_valid_deadline(page)

    expect(page.locator("#taskDeadlineDate")).not_to_have_value("")
    expect(page.locator("#taskDeadlineHour")).not_to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).not_to_have_value("")

    page.locator("#taskSubmitBtn").click()

    # Уведомление об успешном создании
    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Задача добавлена.")

    # Новая задача появилась в списке
    expect(page.locator("#tasksList")).to_contain_text(title)
    expect(page.locator("#tasksList")).to_contain_text(description)

    # Форма очистилась
    expect(page.locator("#taskTitle")).to_have_value("")
    expect(page.locator("#taskDescription")).to_have_value("")
    expect(page.locator("#taskPriority")).to_have_value("medium")
    expect(page.locator("#taskDeadlineDate")).to_have_value("")
    expect(page.locator("#taskDeadlineHour")).to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).to_have_value("")
    
def test_create_task_without_title(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    page.locator("#taskDescription").fill("Task without title")
    page.locator("#taskTitle").click()
    page.locator("#taskDescription").click()

    expect(page.locator("#taskTitleError")).to_be_visible()
    expect(page.locator("#taskTitleError")).to_have_text("Название задачи обязательно.")
    expect(page.locator("#taskTitle")).to_have_class("is-invalid")

    # У описания ошибки быть не должно
    expect(page.locator("#taskDescriptionError")).to_be_hidden()

    # Остаёмся в рабочей зоне, задача не создаётся
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    
def test_create_task_with_title_is_only_spaces(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    page.locator("#taskDescription").fill("Task without title")
    page.locator("#taskTitle").fill("   ")
    page.locator("#taskDescription").click()

    expect(page.locator("#taskTitleError")).to_be_visible()
    expect(page.locator("#taskTitleError")).to_have_text("Название задачи обязательно.")
    expect(page.locator("#taskTitle")).to_have_class("is-invalid")

    # У описания ошибки быть не должно
    expect(page.locator("#taskDescriptionError")).to_be_hidden()

    # Остаёмся в рабочей зоне, показывается inline-ошибка, submit не выполнялся
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    
def test_create_title_is_longer_than_the_allowed_value(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    page.locator("#taskDescription").fill("Task")
    page.locator("#taskTitle").fill("hsdfkhdsjkfsdkjjsdkfjksdkfhjshfjksdjkfhdkfjsdfhdjkfhskjfhdkjhfkjshfjkhsdjfjskfsdhkfsdhkjsdjsdhjksdhjskdhkjsdhfjksdhjksdf")
    page.locator("#taskDescription").click()

    expect(page.locator("#taskTitleError")).to_be_visible()
    expect(page.locator("#taskTitleError")).to_have_text("Название должно быть не длиннее 80 символов.")
    expect(page.locator("#taskTitle")).to_have_class("is-invalid")

    # У описания ошибки быть не должно
    expect(page.locator("#taskDescriptionError")).to_be_hidden()

    # Остаёмся в рабочей зоне, показывается inline-ошибка, submit не выполнялся
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    
def test_create_task_with_title_is_shorter_than_the_maximum_by_1_character(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    title = "testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttettesttest"
    description = "Task created by Playwright smoke test"

    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill(description)
    set_task_priority(page, "high")
    fill_valid_deadline(page)

    expect(page.locator("#taskDeadlineDate")).not_to_have_value("")
    expect(page.locator("#taskDeadlineHour")).not_to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).not_to_have_value("")

    page.locator("#taskSubmitBtn").click()

    # Уведомление об успешном создании
    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Задача добавлена.")

    # Новая задача появилась в списке
    expect(page.locator("#tasksList")).to_contain_text(title)
    expect(page.locator("#tasksList")).to_contain_text(description)

    # Форма очистилась
    expect(page.locator("#taskTitle")).to_have_value("")
    expect(page.locator("#taskDescription")).to_have_value("")
    expect(page.locator("#taskPriority")).to_have_value("medium")
    expect(page.locator("#taskDeadlineDate")).to_have_value("")
    expect(page.locator("#taskDeadlineHour")).to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).to_have_value("")
    
def test_create_task_with_description_is_empty(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    title = "test"
    description = ""

    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill(description)
    set_task_priority(page, "high")
    fill_valid_deadline(page)

    expect(page.locator("#taskDeadlineDate")).not_to_have_value("")
    expect(page.locator("#taskDeadlineHour")).not_to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).not_to_have_value("")

    page.locator("#taskSubmitBtn").click()

    # Уведомление об успешном создании
    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Задача добавлена.")

    # Новая задача появилась в списке
    expect(page.locator("#tasksList")).to_contain_text(title)
    expect(page.locator("#tasksList")).to_contain_text(description)

    # Форма очистилась
    expect(page.locator("#taskTitle")).to_have_value("")
    expect(page.locator("#taskDescription")).to_have_value("")
    expect(page.locator("#taskPriority")).to_have_value("medium")
    expect(page.locator("#taskDeadlineDate")).to_have_value("")
    expect(page.locator("#taskDeadlineHour")).to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).to_have_value("")
    
def test_create_task_with_description_too_long(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    page.locator("#taskTitle").fill(f"task_{username}")
    page.locator("#taskDescription").fill("a" * 501)
    page.locator("#taskTitle").click()

    expect(page.locator("#taskDescriptionError")).to_be_visible()
    expect(page.locator("#taskDescriptionError")).to_have_text("Описание должно быть не длиннее 500 символов.")
    expect(page.locator("#taskDescription")).to_have_class("is-invalid")

    expect(page.locator("#taskTitleError")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    
def test_create_task_with_max_description_length(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    title = f"task_{username}"
    description = "a" * 500

    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill(description)
    page.locator("#taskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Задача добавлена.")
    expect(page.locator("#tasksList")).to_contain_text(title)
    expect(page.locator("#tasksList")).to_contain_text(description)
    
def test_create_task_with_description_one_char_shorter_than_max_length(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    title = f"task_{username}"
    description = "a" * 499

    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill(description)
    page.locator("#taskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Задача добавлена.")
    expect(page.locator("#tasksList")).to_contain_text(title)
    expect(page.locator("#tasksList")).to_contain_text(description)
    
def test_create_task_without_priority_sets_medium_by_default(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    title = f"task_{username}"
    description = "Task without explicit priority"

    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill(description)

    page.locator("#taskPriority").evaluate(
        """el => {
            el.value = "";
            el.dispatchEvent(new Event("change", { bubbles: true }));
        }"""
    )

    page.locator("#taskSubmitBtn").click()

    task_card = page.locator("#tasksList .task-card", has_text=title).first
    expect(task_card).to_be_visible()
    expect(task_card.locator(".badge-priority")).to_contain_text("Средний")
    
def test_create_task_without_deadline_creates_task_without_deadline(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    title = f"task_{username}"
    description = "Task without deadline"

    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill(description)
    page.locator("#taskSubmitBtn").click()

    task_card = page.locator("#tasksList .task-card", has_text=title).first
    expect(task_card).to_be_visible()
    expect(task_card.locator(".badge-deadline")).to_contain_text("Без дедлайна")
    
def test_create_task_with_expired_token(page: Page):
    expired_token = create_expired_token()
    title = "expired_token_task"

    page.goto(BASE_URL)

    page.evaluate(
        """({ token, username }) => {
            window.localStorage.setItem("token", token);
            window.localStorage.setItem("username", username);
        }""",
        {"token": expired_token, "username": "expired_user"},
    )

    page.reload()

    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()

    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill("Task with expired token")
    page.locator("#taskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text("Не удалось создать задачу.")
    expect(page.locator("#tasksList")).not_to_contain_text(title)
    
def test_clear_deadline_field_with_clear_button(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    login_via_ui(page, username, password)

    fill_valid_deadline(page)

    expect(page.locator("#taskDeadlineDate")).not_to_have_value("")
    expect(page.locator("#taskDeadlineHour")).not_to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).not_to_have_value("")

    page.locator("#clearTaskDeadlineBtn").click()

    expect(page.locator("#taskDeadlineDate")).to_have_value("")
    expect(page.locator("#taskDeadlineHour")).to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).to_have_value("")
    expect(page.locator("#taskDeadlineHour")).to_be_disabled()
    expect(page.locator("#taskDeadlineMinute")).to_be_disabled()