from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

import pytest
import requests
from flask_jwt_extended import create_access_token
from playwright.sync_api import Page, expect

from app import create_app

BASE_URL = "http://127.0.0.1:5000"
DEFAULT_PASSWORD = "Password123"


@dataclass
class TestUser:
    username: str
    password: str
    token: str | None = None


def generate_unique_user(prefix: str = "autotest") -> tuple[str, str]:
    suffix = uuid.uuid4().hex[:6]
    return f"{prefix}_{suffix}", DEFAULT_PASSWORD


def register_user_via_api(
    username: str,
    password: str,
    *,
    base_url: str = BASE_URL,
) -> requests.Response:
    response = requests.post(
        f"{base_url}/register",
        json={"username": username, "password": password},
        timeout=10,
    )
    return response


def login_user_via_api(
    username: str,
    password: str,
    *,
    base_url: str = BASE_URL,
) -> requests.Response:
    response = requests.post(
        f"{base_url}/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    return response


def create_task_via_api(
    token: str,
    *,
    title: str,
    description: str = "Task description",
    priority: str = "medium",
    deadline: str | None = None,
    base_url: str = BASE_URL,
) -> requests.Response:
    response = requests.post(
        f"{base_url}/tasks",
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
        timeout=10,
    )
    return response


def update_task_status_via_api(
    token: str,
    task_id: int,
    status: str,
    *,
    base_url: str = BASE_URL,
) -> requests.Response:
    response = requests.patch(
        f"{base_url}/tasks/{task_id}/status",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"status": status},
        timeout=10,
    )
    return response


def create_expired_token() -> str:
    app = create_app()
    with app.app_context():
        return create_access_token(
            identity="1",
            expires_delta=timedelta(seconds=-1),
        )


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def unique_user_credentials() -> tuple[str, str]:
    return generate_unique_user()


@pytest.fixture
def api_user(base_url: str, unique_user_credentials: tuple[str, str]) -> TestUser:
    username, password = unique_user_credentials

    register_response = register_user_via_api(username, password, base_url=base_url)
    assert register_response.status_code == 201, register_response.text

    login_response = login_user_via_api(username, password, base_url=base_url)
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    return TestUser(username=username, password=password, token=token)


@pytest.fixture
def auth_headers(api_user: TestUser) -> dict[str, str]:
    assert api_user.token, "Expected token in api_user fixture"
    return {"Authorization": f"Bearer {api_user.token}"}


@pytest.fixture
def task_factory(base_url: str, api_user: TestUser) -> Callable[..., dict]:
    def _factory(
        *,
        title: str | None = None,
        description: str = "Task description",
        priority: str = "medium",
        deadline: str | None = None,
    ) -> dict:
        task_title = title or f"Task {uuid.uuid4().hex[:6]}"
        response = create_task_via_api(
            api_user.token,
            title=task_title,
            description=description,
            priority=priority,
            deadline=deadline,
            base_url=base_url,
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _factory


@pytest.fixture
def expired_token() -> str:
    return create_expired_token()


@pytest.fixture
def open_login_form(base_url: str) -> Callable[[Page], None]:
    def _open(page: Page) -> None:
        page.goto(base_url)
        expect(page.locator("#loginForm")).to_be_visible()
        expect(page.locator("#registerForm")).to_be_hidden()

    return _open


@pytest.fixture
def login_via_ui(open_login_form: Callable[[Page], None]) -> Callable[[Page, str, str], None]:
    def _login(page: Page, username: str, password: str) -> None:
        open_login_form(page)

        page.locator("#loginUsername").fill(username)
        page.locator("#loginPassword").fill(password)
        page.locator("#loginSubmitBtn").click()

        expect(page.locator("#authSection")).to_be_hidden()
        expect(page.locator("#appSection")).to_be_visible()
        expect(page.locator("#authStatusText")).to_have_text("Авторизован")
        expect(page.locator("#userText")).to_have_text(username)

    return _login


@pytest.fixture
def ui_user(page: Page, api_user: TestUser, login_via_ui: Callable[[Page, str, str], None]) -> TestUser:
    login_via_ui(page, api_user.username, api_user.password)
    return api_user


@pytest.fixture
def task_card() -> Callable[[Page, str], object]:
    def _get_task_card(page: Page, title: str):
        return page.locator("#tasksList .task-card", has_text=title).first

    return _get_task_card


@pytest.fixture
def set_select_value() -> Callable[[Page, str, str], None]:
    def _set(page: Page, selector: str, value: str) -> None:
        page.locator(selector).evaluate(
            """(el, nextValue) => {
                el.value = nextValue;
                el.dispatchEvent(new Event("change", { bubbles: true }));
            }""",
            value,
        )

    return _set


@pytest.fixture
def set_task_priority() -> Callable[[Page, str], None]:
    def _set(page: Page, value: str) -> None:
        page.locator("#taskPriority").evaluate(
            """(el, priorityValue) => {
                el.value = priorityValue;
                el.dispatchEvent(new Event("change", { bubbles: true }));
            }""",
            value,
        )

    return _set


@pytest.fixture
def set_edit_priority() -> Callable[[Page, str], None]:
    def _set(page: Page, value: str) -> None:
        page.locator("#editTaskPriority").evaluate(
            """(el, priorityValue) => {
                el.value = priorityValue;
                el.dispatchEvent(new Event("change", { bubbles: true }));
            }""",
            value,
        )

    return _set


@pytest.fixture
def fill_valid_deadline() -> Callable[[Page], None]:
    def _fill(page: Page) -> None:
        future_date = datetime.now() + timedelta(days=1)
        ui_date = future_date.strftime("%d.%m.%Y")

        page.locator("#taskDeadlineDate").fill(ui_date)
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

    return _fill


@pytest.fixture
def force_edit_deadline() -> Callable[[Page, datetime], None]:
    def _force(page: Page, target_dt: datetime) -> None:
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

    return _force


@pytest.fixture
def create_task_for_user(base_url: str) -> Callable[..., dict]:
    def _create(
        *,
        username: str | None = None,
        password: str = DEFAULT_PASSWORD,
        prefix: str = "uiuser",
        title: str | None = None,
        description: str = "Task description",
        priority: str = "medium",
        deadline: str | None = None,
    ) -> dict:
        actual_username = username or f"{prefix}_{uuid.uuid4().hex[:6]}"

        register_response = register_user_via_api(
            actual_username,
            password,
            base_url=base_url,
        )
        assert register_response.status_code == 201, register_response.text

        login_response = login_user_via_api(
            actual_username,
            password,
            base_url=base_url,
        )
        assert login_response.status_code == 200, login_response.text

        token = login_response.json()["access_token"]

        task_response = create_task_via_api(
            token,
            title=title or f"Task {uuid.uuid4().hex[:6]}",
            description=description,
            priority=priority,
            deadline=deadline,
            base_url=base_url,
        )
        assert task_response.status_code == 201, task_response.text

        return {
            "username": actual_username,
            "password": password,
            "token": token,
            "task": task_response.json(),
        }

    return _create
