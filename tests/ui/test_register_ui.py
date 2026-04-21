import uuid

import pytest
from playwright.sync_api import expect


def generate_username(length=6, prefix="uiuser"):
    return f"{prefix}_{uuid.uuid4().hex[:length]}"


def open_register_form(page, open_login_form):
    open_login_form(page)
    page.locator('[data-auth-mode="register"]').click()
    expect(page.locator("#registerForm")).to_be_visible()
    expect(page.locator("#loginForm")).to_be_hidden()


def assert_auth_screen(page):
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()


def assert_authorized(page, username):
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(username)
    expect(page.locator("#logoutBtn")).to_be_visible()


@pytest.mark.parametrize(
    ("username", "password"),
    [
        (None, "Password123"),
        (None, "Password123121212121212121212121"),
        ("dynamic_min", "Passwo12"),
    ],
)
def test_successful_registration(page, open_login_form, username, password):
    if username is None:
        username = generate_username()
    elif username == "dynamic_min":
        username = f"u{uuid.uuid4().hex[:2]}"

    open_register_form(page, open_login_form)

    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)
    page.locator("#registerSubmitBtn").click()

    assert_authorized(page, username)

    saved_username = page.evaluate("window.localStorage.getItem('username')")
    saved_token = page.evaluate("window.localStorage.getItem('token')")

    assert saved_username == username
    assert saved_token


def test_registration_with_existing_username(page, open_login_form):
    username = generate_username()
    password = "Password123"

    open_register_form(page, open_login_form)
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)
    page.locator("#registerSubmitBtn").click()

    assert_authorized(page, username)

    page.locator("#logoutBtn").click()
    assert_auth_screen(page)

    page.locator('[data-auth-mode="register"]').click()
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)
    page.locator("#registerSubmitBtn").click()

    expect(page.locator("#registerUsernameError")).to_be_visible()
    expect(page.locator("#registerUsernameError")).to_have_text("Такой логин уже существует.")
    expect(page.locator("#registerUsername")).to_have_class("is-invalid")
    expect(page.locator("#registerPasswordError")).to_be_hidden()
    expect(page.locator("#registerUsername")).to_be_focused()
    assert_auth_screen(page)


@pytest.mark.parametrize(
    ("username", "password", "username_error", "password_error"),
    [
        ("", "Password123", "Логин обязателен.", None),
        ("validuser123", "", None, "Пароль обязателен."),
        ("user name", "Password123", "Логин не должен содержать пробелы.", None),
        ("userимя", "Password123", "Логин не должен содержать кириллицу.", None),
        (f"uiuser_{'a' * 29}", "Password123", "Логин должен быть от 3 до 30 символов.", None),
        ("a2", "Password123", "Логин должен быть от 3 до 30 символов.", None),
        (None, "Pasw23", None, "Пароль должен быть от 8 до 32 символов."),
        (None, "Pasw23qwqwqw12121sqwtwrtweweqqq1233455", None, "Пароль должен быть от 8 до 32 символов."),
        (None, "Pasw23or d1 123", None, "Пароль не должен содержать пробелы."),
        (None, "123412345678", None, "Пароль должен содержать хотя бы одну латинскую букву."),
        (None, "lettersletters", None, "Пароль должен содержать хотя бы одну цифру."),
        (None, "lettersкириллица", None, "Пароль не должен содержать кириллицу."),
    ],
)
def test_registration_inline_validation(page, open_login_form, username, password, username_error, password_error):
    if username is None:
        username = generate_username()

    open_register_form(page, open_login_form)

    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)

    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    if username_error:
        expect(page.locator("#registerUsernameError")).to_be_visible()
        expect(page.locator("#registerUsernameError")).to_have_text(username_error)
        expect(page.locator("#registerUsername")).to_have_class("is-invalid")
    else:
        expect(page.locator("#registerUsernameError")).to_be_hidden()

    if password_error:
        expect(page.locator("#registerPasswordError")).to_be_visible()
        expect(page.locator("#registerPasswordError")).to_have_text(password_error)
        expect(page.locator("#registerPassword")).to_have_class("is-invalid")
    else:
        expect(page.locator("#registerPasswordError")).to_be_hidden()

    assert_auth_screen(page)


def test_switch_from_register_form_to_login_form(page, open_login_form):
    open_register_form(page, open_login_form)

    page.locator('[data-auth-mode="login"]').click()

    expect(page.locator("#loginForm")).to_be_visible()
    expect(page.locator("#registerForm")).to_be_hidden()
    assert_auth_screen(page)


def test_theme_toggle_from_light_to_dark_and_back_preserves_register_fields(page, open_login_form):
    username = generate_username()
    password = "Password123"

    open_register_form(page, open_login_form)

    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)

    page.locator("#themeToggleBtn").click()

    expect(page.locator("body")).to_have_attribute("data-theme", "dark")
    expect(page.locator("#registerUsername")).to_have_value(username)
    expect(page.locator("#registerPassword")).to_have_value(password)

    page.locator("#themeToggleBtn").click()

    expect(page.locator("body")).to_have_attribute("data-theme", "light")
    expect(page.locator("#registerUsername")).to_have_value(username)
    expect(page.locator("#registerPassword")).to_have_value(password)
    assert_auth_screen(page)
