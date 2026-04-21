import uuid

import pytest
from playwright.sync_api import expect


@pytest.fixture
def delete_ready(page, api_user, task_factory, login_via_ui, task_card):
    def _ready(title=None):
        task_title = title or f"Task {uuid.uuid4().hex[:6]}"
        task_factory(
            title=task_title,
            description="Task for delete modal tests",
            priority="medium",
        )
        login_via_ui(page, api_user.username, api_user.password)

        card = task_card(page, task_title)
        expect(card).to_be_visible()

        return {
            "username": api_user.username,
            "password": api_user.password,
            "title": task_title,
            "task_card": card,
        }

    return _ready


def open_delete_modal(data, page):
    data["task_card"].locator('[data-action="delete"]').click()
    expect(page.locator("#deleteModal")).to_be_visible()


def test_successful_task_deletion(page, delete_ready):
    data = delete_ready()

    open_delete_modal(data, page)
    page.locator("#confirmDeleteBtn").click()

    expect(page.locator("#deleteModal")).to_be_hidden()
    expect(page.locator("#messageBox")).to_have_text("Задача удалена.")
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    expect(page.locator("#tasksList")).not_to_contain_text(data["title"])


@pytest.mark.parametrize(
    "action",
    ["escape", "close_button", "backdrop", "cancel"],
)
def test_delete_modal_can_be_closed_in_multiple_ways(page, delete_ready, action):
    data = delete_ready()

    open_delete_modal(data, page)

    if action == "escape":
        page.keyboard.press("Escape")
    elif action == "close_button":
        page.locator("#closeDeleteModalBtn").click()
    elif action == "backdrop":
        page.locator('#deleteModal [data-close-delete-modal="true"]').click(position={"x": 5, "y": 5})
    else:
        page.locator("#cancelDeleteBtn").click()

    expect(page.locator("#deleteModal")).to_be_hidden()
    expect(page.locator("#tasksList")).to_contain_text(data["title"])


def test_delete_task_with_expired_token_logs_out_user_and_keeps_task(page, delete_ready, expired_token, login_via_ui):
    data = delete_ready()

    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )

    open_delete_modal(data, page)
    page.locator("#confirmDeleteBtn").click()

    expect(page.locator("#messageBox")).to_have_text("Сессия истекла. Войдите снова.")
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    expect(page.locator("#deleteModal")).to_be_hidden()

    login_via_ui(page, data["username"], data["password"])
    expect(page.locator("#tasksList")).to_contain_text(data["title"])


def test_delete_modal_shows_exact_task_title(page, delete_ready):
    title = f"Delete me {uuid.uuid4().hex[:6]}"
    data = delete_ready(title=title)

    open_delete_modal(data, page)

    expect(page.locator("#deleteModalTaskText")).to_have_text(f"Задача: {title}")
