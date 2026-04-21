import uuid

import pytest
from playwright.sync_api import expect


@pytest.fixture
def logged_in_user(page, api_user, login_via_ui):
    login_via_ui(page, api_user.username, api_user.password)
    return api_user


def fill_create_form(page, *, title="", description="", priority=None, with_deadline=False, set_task_priority=None, fill_valid_deadline=None):
    page.locator("#taskTitle").fill(title)
    page.locator("#taskDescription").fill(description)

    if priority is not None and set_task_priority is not None:
        set_task_priority(page, priority)

    if with_deadline and fill_valid_deadline is not None:
        fill_valid_deadline(page)


def assert_create_form_cleared(page):
    expect(page.locator("#taskTitle")).to_have_value("")
    expect(page.locator("#taskDescription")).to_have_value("")
    expect(page.locator("#taskPriority")).to_have_value("medium")
    expect(page.locator("#taskDeadlineDate")).to_have_value("")
    expect(page.locator("#taskDeadlineHour")).to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).to_have_value("")


def assert_still_in_workspace(page):
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()


def test_create_task_with_all_valid_fields(logged_in_user, page, set_task_priority, fill_valid_deadline):
    title = f"UI task {uuid.uuid4().hex[:6]}"
    description = "Task created by Playwright smoke test"

    fill_create_form(
        page,
        title=title,
        description=description,
        priority="high",
        with_deadline=True,
        set_task_priority=set_task_priority,
        fill_valid_deadline=fill_valid_deadline,
    )

    expect(page.locator("#taskDeadlineDate")).not_to_have_value("")
    expect(page.locator("#taskDeadlineHour")).not_to_have_value("")
    expect(page.locator("#taskDeadlineMinute")).not_to_have_value("")

    page.locator("#taskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_have_text("Задача добавлена.")
    expect(page.locator("#tasksList")).to_contain_text(title)
    expect(page.locator("#tasksList")).to_contain_text(description)
    assert_create_form_cleared(page)


@pytest.mark.parametrize(
    ("title", "description", "error_text"),
    [
        ("", "Task without title", "Название задачи обязательно."),
        ("   ", "Task without title", "Название задачи обязательно."),
        ("hsdfkhdsjkfsdkjjsdkfjksdkfhjshfjksdjkfhdkfjsdfhdjkfhskjfhdkjhfkjshfjkhsdjfjskfsdhkfsdhkjsdjsdhjksdhjskdhkjsdhfjksdhjksdf", "Task", "Название должно быть не длиннее 80 символов."),
    ],
)
def test_create_task_invalid_title_values_show_inline_error(logged_in_user, page, title, description, error_text):
    fill_create_form(page, title=title, description=description)

    if title == "":
        page.locator("#taskTitle").click()
    page.locator("#taskDescription").click()

    expect(page.locator("#taskTitleError")).to_be_visible()
    expect(page.locator("#taskTitleError")).to_have_text(error_text)
    expect(page.locator("#taskTitle")).to_have_class("is-invalid")
    expect(page.locator("#taskDescriptionError")).to_be_hidden()
    assert_still_in_workspace(page)


@pytest.mark.parametrize(
    ("title", "description", "use_deadline"),
    [
        ("testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttettesttest", "Task created by Playwright smoke test", True),
        ("test", "", True),
        ("task_max_desc", "a" * 500, False),
        ("task_499_desc", "a" * 499, False),
    ],
)
def test_create_task_valid_boundaries_and_optional_description(
    logged_in_user,
    page,
    set_task_priority,
    fill_valid_deadline,
    title,
    description,
    use_deadline,
):
    fill_create_form(
        page,
        title=title,
        description=description,
        priority="high" if use_deadline else None,
        with_deadline=use_deadline,
        set_task_priority=set_task_priority,
        fill_valid_deadline=fill_valid_deadline,
    )

    page.locator("#taskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_have_text("Задача добавлена.")
    expect(page.locator("#tasksList")).to_contain_text(title)
    assert_create_form_cleared(page)


def test_create_task_description_too_long(logged_in_user, page):
    fill_create_form(page, title=f"task_{logged_in_user.username}", description="a" * 501)
    page.locator("#taskTitle").click()

    expect(page.locator("#taskDescriptionError")).to_be_visible()
    expect(page.locator("#taskDescriptionError")).to_have_text("Описание должно быть не длиннее 500 символов.")
    expect(page.locator("#taskDescription")).to_have_class("is-invalid")
    expect(page.locator("#taskTitleError")).to_be_hidden()
    assert_still_in_workspace(page)


def test_create_task_without_priority_sets_medium_by_default(logged_in_user, page):
    title = f"task_{logged_in_user.username}"
    fill_create_form(page, title=title, description="Task without explicit priority")

    page.locator("#taskPriority").evaluate(
        """el => {
            el.value = "";
            el.dispatchEvent(new Event("change", { bubbles: true }));
        }"""
    )
    page.locator("#taskSubmitBtn").click()

    card = page.locator("#tasksList .task-card", has_text=title).first
    expect(card).to_be_visible()
    expect(card.locator(".badge-priority")).to_contain_text("Средний")


def test_create_task_without_deadline_creates_task_without_deadline(logged_in_user, page):
    title = f"task_{logged_in_user.username}"
    fill_create_form(page, title=title, description="Task without deadline")
    page.locator("#taskSubmitBtn").click()

    card = page.locator("#tasksList .task-card", has_text=title).first
    expect(card).to_be_visible()
    expect(card.locator(".badge-deadline")).to_contain_text("Без дедлайна")


def test_create_task_with_expired_token(logged_in_user, page, login_via_ui, expired_token):
    title = f"Expired create {uuid.uuid4().hex[:6]}"
    fill_create_form(page, title=title, description="Task should not be created")

    page.evaluate(
        """token => {
            state.token = token;
            window.localStorage.setItem("token", token);
        }""",
        expired_token,
    )
    page.locator("#taskSubmitBtn").click()

    expect(page.locator("#messageBox")).to_have_text("Сессия истекла. Войдите снова.")
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    expect(page.locator("#authStatusText")).to_have_text("Не авторизован")
    expect(page.locator("#userText")).to_have_text("—")

    login_via_ui(page, logged_in_user.username, logged_in_user.password)
    expect(page.locator("#tasksList")).not_to_contain_text(title)


def test_clear_deadline_field_with_clear_button(logged_in_user, page, fill_valid_deadline):
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
