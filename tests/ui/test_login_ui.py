import uuid
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
    

def test_successful_login(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)

    open_login_form(page)

    page.locator("#loginUsername").fill(username)
    page.locator("#loginPassword").fill(password)
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()

    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(username)
    expect(page.locator("#logoutBtn")).to_be_visible()

    saved_username = page.evaluate("window.localStorage.getItem('username')")
    saved_token = page.evaluate("window.localStorage.getItem('token')")

    assert saved_username == username
    assert saved_token is not None
    assert saved_token != ""
    
def test_login_with_invalid_login(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    open_login_form(page)

    page.locator("#loginUsername").fill("Wronglogin123")
    page.locator("#loginPassword").fill(password)
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#loginPasswordError")).to_be_visible()
    expect(page.locator("#loginPasswordError")).to_have_text("Неверный логин или пароль.")

    expect(page.locator("#loginUsername")).to_have_class("is-invalid")
    expect(page.locator("#loginPassword")).to_have_class("is-invalid")

    expect(page.locator("#loginUsernameError")).to_be_hidden()

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_login_with_invalid_password(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    open_login_form(page)

    page.locator("#loginUsername").fill(username)
    page.locator("#loginPassword").fill("Wrongpass123")
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#loginPasswordError")).to_be_visible()
    expect(page.locator("#loginPasswordError")).to_have_text("Неверный логин или пароль.")

    expect(page.locator("#loginUsername")).to_have_class("is-invalid")
    expect(page.locator("#loginPassword")).to_have_class("is-invalid")

    expect(page.locator("#loginUsernameError")).to_be_hidden()

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_login_with_invalid_login_and_password(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    open_login_form(page)

    page.locator("#loginUsername").fill("wrong1username")
    page.locator("#loginPassword").fill("Wrongpass123")
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#loginPasswordError")).to_be_visible()
    expect(page.locator("#loginPasswordError")).to_have_text("Неверный логин или пароль.")

    expect(page.locator("#loginUsername")).to_have_class("is-invalid")
    expect(page.locator("#loginPassword")).to_have_class("is-invalid")

    expect(page.locator("#loginUsernameError")).to_be_hidden()

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_login_without_username(page: Page):
    open_login_form(page)

    page.locator("#loginPassword").fill("Password123")

    page.locator("#loginUsername").click()
    page.locator("#loginPassword").click()

    expect(page.locator("#loginUsernameError")).to_be_visible()
    expect(page.locator("#loginUsernameError")).to_have_text("Логин обязателен.")

    expect(page.locator("#loginUsername")).to_have_class("is-invalid")
    expect(page.locator("#loginPasswordError")).to_be_hidden()

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_login_without_password(page: Page):
    open_login_form(page)

    page.locator("#loginUsername").fill("Username123")

    page.locator("#loginPassword").click()
    page.locator("#loginUsername").click()

    expect(page.locator("#loginPasswordError")).to_be_visible()
    expect(page.locator("#loginPasswordError")).to_have_text("Пароль обязателен.")

    expect(page.locator("#loginPassword")).to_have_class("is-invalid")
    expect(page.locator("#loginUsernameError")).to_be_hidden()

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_login_without_username_and_password(page: Page):
    open_login_form(page)

    # Трогаем оба поля и уводим фокус, чтобы сработала inline-валидация
    page.locator("#loginUsername").click()
    page.locator("#loginPassword").click()
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#loginUsernameError")).to_be_visible()
    expect(page.locator("#loginUsernameError")).to_have_text("Логин обязателен.")
    expect(page.locator("#loginPasswordError")).to_be_visible()
    expect(page.locator("#loginPasswordError")).to_have_text("Пароль обязателен.")

    expect(page.locator("#loginUsername")).to_have_class("is-invalid")
    expect(page.locator("#loginPassword")).to_have_class("is-invalid")

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_login_with_spaces_in_password(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    open_login_form(page)

    page.locator("#loginUsername").fill(username)
    page.locator("#loginPassword").fill("Wrong pass123")
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#loginPasswordError")).to_be_visible()
    expect(page.locator("#loginPasswordError")).to_have_text("Пароль не должен содержать пробелы.")

    expect(page.locator("#loginPassword")).to_have_class("is-invalid")

    expect(page.locator("#loginUsernameError")).to_be_hidden()

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_login_with_spaces_in_username(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    open_login_form(page)

    page.locator("#loginUsername").fill("usern ame123")
    page.locator("#loginPassword").fill(password)
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#loginUsernameError")).to_be_visible()
    expect(page.locator("#loginUsernameError")).to_have_text("Логин не должен содержать пробелы.")

    expect(page.locator("#loginUsername")).to_have_class("is-invalid")

    expect(page.locator("#loginPasswordError")).to_be_hidden()

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_switch_from_login_form_to_register_form(page: Page):
    open_login_form(page)

    expect(page.locator("#loginForm")).to_be_visible()
    expect(page.locator("#registerForm")).to_be_hidden()

    page.locator('[data-auth-mode="register"]').click()

    expect(page.locator("#registerForm")).to_be_visible()
    expect(page.locator("#loginForm")).to_be_hidden()

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_theme_toggle_from_light_to_dark_and_back_preserves_login_fields(page: Page):
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

    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()