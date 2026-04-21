import pytest
from playwright.sync_api import expect


def assert_auth_screen(page):
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()


def test_successful_login(page, api_user, open_login_form):
    open_login_form(page)

    page.locator("#loginUsername").fill(api_user.username)
    page.locator("#loginPassword").fill(api_user.password)
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(api_user.username)
    expect(page.locator("#logoutBtn")).to_be_visible()

    saved_username = page.evaluate("window.localStorage.getItem('username')")
    saved_token = page.evaluate("window.localStorage.getItem('token')")

    assert saved_username == api_user.username
    assert saved_token


@pytest.mark.parametrize(
    ("username_value", "password_value"),
    [
        ("Wronglogin123", "Password123"),
        ("validuser", "Wrongpass123"),
        ("wrong1username", "Wrongpass123"),
    ],
)
def test_login_with_invalid_credentials(page, api_user, open_login_form, username_value, password_value):
    open_login_form(page)

    page.locator("#loginUsername").fill(
        api_user.username if username_value == "validuser" else username_value
    )
    page.locator("#loginPassword").fill(
        api_user.password if password_value == "Password123" else password_value
    )
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#loginPasswordError")).to_be_visible()
    expect(page.locator("#loginPasswordError")).to_have_text("Неверный логин или пароль.")
    expect(page.locator("#loginUsername")).to_have_class("is-invalid")
    expect(page.locator("#loginPassword")).to_have_class("is-invalid")
    expect(page.locator("#loginUsernameError")).to_be_hidden()
    assert_auth_screen(page)


@pytest.mark.parametrize(
    ("username_value", "password_value", "username_error", "password_error"),
    [
        ("", "Password123", "Логин обязателен.", None),
        ("Username123", "", None, "Пароль обязателен."),
        ("", "", "Логин обязателен.", "Пароль обязателен."),
        ("usern ame123", "Password123", "Логин не должен содержать пробелы.", None),
        ("validuser123", "Wrong pass123", None, "Пароль не должен содержать пробелы."),
    ],
)
def test_login_inline_validation(page, open_login_form, username_value, password_value, username_error, password_error):
    open_login_form(page)

    if username_value:
        page.locator("#loginUsername").fill(username_value)
    if password_value:
        page.locator("#loginPassword").fill(password_value)

    page.locator("#loginUsername").click()
    page.locator("#loginPassword").click()
    page.locator("#loginSubmitBtn").click()

    if username_error:
        expect(page.locator("#loginUsernameError")).to_be_visible()
        expect(page.locator("#loginUsernameError")).to_have_text(username_error)
        expect(page.locator("#loginUsername")).to_have_class("is-invalid")
    else:
        expect(page.locator("#loginUsernameError")).to_be_hidden()

    if password_error:
        expect(page.locator("#loginPasswordError")).to_be_visible()
        expect(page.locator("#loginPasswordError")).to_have_text(password_error)
        expect(page.locator("#loginPassword")).to_have_class("is-invalid")
    else:
        expect(page.locator("#loginPasswordError")).to_be_hidden()

    assert_auth_screen(page)


def test_switch_from_login_form_to_register_form(page, open_login_form):
    open_login_form(page)

    expect(page.locator("#loginForm")).to_be_visible()
    expect(page.locator("#registerForm")).to_be_hidden()

    page.locator('[data-auth-mode="register"]').click()

    expect(page.locator("#registerForm")).to_be_visible()
    expect(page.locator("#loginForm")).to_be_hidden()
    assert_auth_screen(page)


def test_theme_toggle_from_light_to_dark_and_back_preserves_login_fields(page, open_login_form):
    page.add_init_script("window.localStorage.setItem('theme', 'light');")
    open_login_form(page)

    username = "validuser123"
    password = "Password123"

    expect(page.locator("body")).to_have_attribute("data-theme", "light")

    page.locator("#loginUsername").fill(username)
    page.locator("#loginPassword").fill(password)

    page.locator("#themeToggleBtn").click()

    expect(page.locator("body")).to_have_attribute("data-theme", "dark")
    expect(page.locator("#loginUsername")).to_have_value(username)
    expect(page.locator("#loginPassword")).to_have_value(password)

    page.locator("#themeToggleBtn").click()

    expect(page.locator("body")).to_have_attribute("data-theme", "light")
    expect(page.locator("#loginUsername")).to_have_value(username)
    expect(page.locator("#loginPassword")).to_have_value(password)
    assert_auth_screen(page)
