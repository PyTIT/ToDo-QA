import uuid
from datetime import datetime, timedelta

import pytest
from playwright.sync_api import expect


def open_edit_modal(page, task_card, title):
    card = task_card(page, title)
    expect(card).to_be_visible()
    card.locator('[data-action="edit"]').click()
    expect(page.locator("#editModal")).to_be_visible()
    return card


@pytest.fixture
def opened_task(api_user, task_factory, login_via_ui, task_card):
    def _open(page, **kwargs):
        title = kwargs.pop("title", None) or f"Task {uuid.uuid4().hex[:6]}"
        task = task_factory(title=title, **kwargs)

        login_via_ui(page, api_user.username, api_user.password)
        card = open_edit_modal(page, task_card, title)

        return {
            "task": task,
            "title": title,
            "username": api_user.username,
            "password": api_user.password,
            "card": card,
        }

    return _open


def test_edit_task_title_with_another_valid_value(page, opened_task):
    data = opened_task(page, description="Smoke edit task")
    new_title = f"Updated {uuid.uuid4().hex[:6]}"

    page.locator("#editTaskTitle").fill(new_title)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_title)
    expect(page.locator("#tasksList")).not_to_contain_text(data["title"])


def test_open_edit_modal_contains_existing_task_data(page, opened_task):
    deadline = (datetime.now() + timedelta(days=1)).replace(second=0, microsecond=0).isoformat()
    title = f"Task {uuid.uuid4().hex[:6]}"
    description = "Existing task description"

    opened_task(
        page,
        title=title,
        description=description,
        priority="high",
        deadline=deadline,
    )

    expect(page.locator("#editTaskTitle")).to_have_value(title)
    expect(page.locator("#editTaskDescription")).to_have_value(description)
    expect(page.locator("#editTaskPriority")).to_have_value("high")
    expect(page.locator("#editTaskDeadlineDate")).not_to_have_value("")
    expect(page.locator("#editTaskTitle")).to_be_focused()


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("   ", "Название задачи обязательно."),
        ("", "Название задачи обязательно."),
        ("121121121121121121121121121121121121121121121121121121121121121121121121121121121",
         "Название должно быть не длиннее 80 символов."),
    ],
)
def test_edit_task_title_invalid_values_show_inline_error(page, opened_task, value, message):
    opened_task(page, description="Task for invalid title edit")

    page.locator("#editTaskTitle").fill(value)
    page.locator("#editTaskDescription").click()

    expect(page.locator("#editTaskTitleError")).to_be_visible()
    expect(page.locator("#editTaskTitleError")).to_have_text(message)
    expect(page.locator("#editTaskTitle")).to_have_class("is-invalid")
    expect(page.locator("#editModal")).to_be_visible()


@pytest.mark.parametrize("length", [79, 80])
def test_edit_task_title_boundaries(page, opened_task, length):
    new_title = "a" * length
    opened_task(page)

    page.locator("#editTaskTitle").fill(new_title)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_title)


def test_edit_task_description_with_another_valid_value(page, opened_task):
    new_description = "Updated description from Playwright"
    opened_task(page)

    page.locator("#editTaskDescription").fill(new_description)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_description)


def test_edit_task_with_empty_description(page, opened_task, task_card):
    data = opened_task(page, description="Initial description")

    page.locator("#editTaskDescription").fill("")
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(task_card(page, data["title"])).to_contain_text("Без описания")


def test_edit_task_description_too_long(page, opened_task):
    opened_task(page)

    page.locator("#editTaskDescription").fill("a" * 501)
    page.locator("#editTaskTitle").click()

    expect(page.locator("#editTaskDescriptionError")).to_be_visible()
    expect(page.locator("#editTaskDescriptionError")).to_have_text("Описание должно быть не длиннее 500 символов.")
    expect(page.locator("#editTaskDescription")).to_have_class("is-invalid")
    expect(page.locator("#editModal")).to_be_visible()


@pytest.mark.parametrize("length", [499, 500])
def test_edit_task_description_boundaries(page, opened_task, length):
    new_description = "a" * length
    opened_task(page)

    page.locator("#editTaskDescription").fill(new_description)
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(page.locator("#tasksList")).to_contain_text(new_description)


def test_edit_task_priority_with_another_valid_value(page, opened_task, task_card, set_edit_priority):
    data = opened_task(page, priority="medium")

    set_edit_priority(page, "high")
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(task_card(page, data["title"]).locator(".badge-priority")).to_contain_text("Высокий")


def test_edit_task_deadline_less_than_30_minutes_shows_error(page, opened_task, force_edit_deadline):
    opened_task(page)

    force_edit_deadline(page, datetime.now() + timedelta(minutes=10))
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editTaskDeadlineError")).to_be_visible()
    expect(page.locator("#editTaskDeadlineError")).to_have_text("Дедлайн должен быть минимум на 30 минут позже текущего времени.")
    expect(page.locator("#editModal")).to_be_visible()


def test_edit_task_clear_deadline(page, opened_task, task_card):
    deadline = (datetime.now() + timedelta(days=1)).replace(second=0, microsecond=0).isoformat()
    data = opened_task(page, deadline=deadline)

    page.locator("#clearEditDeadlineBtn").click()
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(task_card(page, data["title"])).to_contain_text("Без дедлайна")


def test_edit_task_change_deadline_to_valid_value(page, opened_task, task_card, force_edit_deadline):
    data = opened_task(page)

    force_edit_deadline(page, datetime.now() + timedelta(days=1, hours=1))
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача обновлена.")
    expect(task_card(page, data["title"])).not_to_contain_text("Без дедлайна")


def test_open_edit_modal_for_task_without_deadline(page, opened_task):
    opened_task(page, deadline=None)

    expect(page.locator("#editTaskDeadlineDate")).to_have_value("")
    expect(page.locator("#editTaskDeadlineHour")).to_have_value("")
    expect(page.locator("#editTaskDeadlineMinute")).to_have_value("")


@pytest.mark.parametrize(
    "action",
    ["#cancelEditBtn", "Escape", "#closeEditModalBtn", '#editModal [data-close-modal="true"]'],
)
def test_edit_modal_can_be_closed_in_multiple_ways(page, opened_task, action):
    opened_task(page)

    if action == "Escape":
        page.keyboard.press(action)
    elif action == '#editModal [data-close-modal="true"]':
        page.locator(action).click(position={"x": 5, "y": 5})
    else:
        page.locator(action).click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()


def test_edit_task_without_changes_shows_no_changes_message(page, opened_task):
    opened_task(page)

    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#editModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Изменений нет.")


def test_edit_task_with_expired_token_shows_error(page, opened_task, expired_token):
    opened_task(page)
    new_title = f"Updated {uuid.uuid4().hex[:6]}"

    page.locator("#editTaskTitle").fill(new_title)
    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_have_text("Сессия истекла. Войдите снова.")
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    expect(page.locator("#authStatusText")).to_have_text("Не авторизован")
    expect(page.locator("#userText")).to_have_text("—")
    expect(page.locator("#editModal")).to_be_hidden()


def test_task_card_does_not_change_after_unsuccessful_edit(
    page,
    opened_task,
    expired_token,
    login_via_ui,
    task_card,
):
    data = opened_task(page)
    new_title = f"Should not be saved {uuid.uuid4().hex[:6]}"

    page.locator("#editTaskTitle").fill(new_title)
    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )
    page.locator("#editTaskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_have_text("Сессия истекла. Войдите снова.")
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()

    login_via_ui(page, data["username"], data["password"])
    expect(task_card(page, data["title"])).to_be_visible()
    expect(page.locator("#tasksList")).not_to_contain_text(new_title)
