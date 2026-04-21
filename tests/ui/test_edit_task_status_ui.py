import re
import uuid

from playwright.sync_api import Page, expect


def setup_user_and_task_for_status(
    page: Page,
    api_user,
    task_factory,
    login_via_ui,
    task_card,
    *,
    title: str | None = None,
):
    task_title = title or f"Task {uuid.uuid4().hex[:6]}"

    task_factory(
        title=task_title,
        description="Task for status change",
        priority="medium",
    )

    login_via_ui(page, api_user.username, api_user.password)

    current_task_card = task_card(page, task_title)
    expect(current_task_card).to_be_visible()

    return {
        "username": api_user.username,
        "password": api_user.password,
        "title": task_title,
        "task_card": current_task_card,
    }


def test_change_task_status_to_another(
    page: Page,
    api_user,
    task_factory,
    login_via_ui,
    task_card,
):
    data = setup_user_and_task_for_status(
        page,
        api_user,
        task_factory,
        login_via_ui,
        task_card,
    )
    current_task_card = data["task_card"]

    current_task_card.locator(
        '[data-action="status"][data-status="in_progress"]'
    ).click()

    expect(page.locator("#messageBox")).to_have_text("Статус обновлён.")
    expect(current_task_card.locator(".badge-status")).to_have_text("В работе")
    expect(
        current_task_card.locator(
            '[data-action="status"][data-status="in_progress"]'
        )
    ).to_have_class(re.compile(r".*is-current.*"))


def test_change_task_status_to_the_same(
    page: Page,
    api_user,
    task_factory,
    login_via_ui,
    task_card,
):
    data = setup_user_and_task_for_status(
        page,
        api_user,
        task_factory,
        login_via_ui,
        task_card,
    )
    current_task_card = data["task_card"]

    current_task_card.locator(
        '[data-action="status"][data-status="new"]'
    ).click()

    expect(page.locator("#messageBox")).to_have_text("Статус обновлён.")
    expect(current_task_card.locator(".badge-status")).to_have_text("Новая")
    expect(
        current_task_card.locator('[data-action="status"][data-status="new"]')
    ).to_have_class(re.compile(r".*is-current.*"))


def test_change_task_status_with_expired_token(
    page: Page,
    api_user,
    task_factory,
    login_via_ui,
    task_card,
    expired_token: str,
):
    data = setup_user_and_task_for_status(
        page,
        api_user,
        task_factory,
        login_via_ui,
        task_card,
    )

    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )

    data["task_card"].locator('[data-action="status"][data-status="done"]').click()

    expect(page.locator("#messageBox")).to_be_visible()
    expect(page.locator("#messageBox")).to_have_text(
        "Сессия истекла. Войдите снова."
    )

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    expect(page.locator("#authStatusText")).to_have_text("Не авторизован")
    expect(page.locator("#userText")).to_have_text("—")

    login_via_ui(page, data["username"], data["password"])

    current_task_card = task_card(page, data["title"])
    expect(current_task_card).to_be_visible()
    expect(current_task_card.locator(".badge-status")).to_have_text("Новая")
    expect(
        current_task_card.locator('[data-action="status"][data-status="new"]')
    ).to_have_class(re.compile(r".*is-current.*"))
