import uuid
import requests
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://127.0.0.1:5000"


def generate_unique_user():
    suffix = uuid.uuid4().hex[:6]
    username = f"uiuser_{suffix}"
    password = "Password123"
    return username, password

def open_register_form(page: Page):
    page.goto(BASE_URL)
    page.locator('[data-auth-mode="register"]').click()
    expect(page.locator("#registerForm")).to_be_visible()

def test_successful_user_registration(page: Page):
    username, password = generate_unique_user()

    page.goto(BASE_URL)

    # Переключаемся на форму регистрации
    page.locator('[data-auth-mode="register"]').click()

    expect(page.locator("#registerForm")).to_be_visible()
    expect(page.locator("#loginForm")).to_be_hidden()

    # Заполняем форму
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)

    # Отправляем
    page.locator("#registerSubmitBtn").click()

    # После успешной регистрации выполняется автологин
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()

    # Проверяем, что пользователь авторизован
    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(username)
    expect(page.locator("#logoutBtn")).to_be_visible()

    # Проверяем localStorage
    saved_username = page.evaluate("window.localStorage.getItem('username')")
    saved_token = page.evaluate("window.localStorage.getItem('token')")

    assert saved_username == username
    assert saved_token is not None
    assert saved_token != ""
    
def test_successful_user_registration_with_login_and_password_is_max_lenght(page: Page):
    suffix = uuid.uuid4().hex[:23]
    username = f"uiuser_{suffix}"
    password = "Password123121212121212121212121"

    page.goto(BASE_URL)

    # Переключаемся на форму регистрации
    page.locator('[data-auth-mode="register"]').click()

    expect(page.locator("#registerForm")).to_be_visible()
    expect(page.locator("#loginForm")).to_be_hidden()

    # Заполняем форму
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)

    # Отправляем
    page.locator("#registerSubmitBtn").click()

    # После успешной регистрации выполняется автологин
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()

    # Проверяем, что пользователь авторизован
    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(username)
    expect(page.locator("#logoutBtn")).to_be_visible()

    # Проверяем localStorage
    saved_username = page.evaluate("window.localStorage.getItem('username')")
    saved_token = page.evaluate("window.localStorage.getItem('token')")

    assert saved_username == username
    assert saved_token is not None
    assert saved_token != ""
    
def test_successful_registration_with_min_length(page: Page):
    suffix = uuid.uuid4().hex[:2]
    username = f"u{suffix}"
    password = "Passwo12"

    page.goto(BASE_URL)

    # Переключаемся на форму регистрации
    page.locator('[data-auth-mode="register"]').click()

    expect(page.locator("#registerForm")).to_be_visible()
    expect(page.locator("#loginForm")).to_be_hidden()

    # Заполняем форму
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)

    # Отправляем
    page.locator("#registerSubmitBtn").click()

    # После успешной регистрации выполняется автологин
    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()

    # Проверяем, что пользователь авторизован
    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(username)
    expect(page.locator("#logoutBtn")).to_be_visible()

    # Проверяем localStorage
    saved_username = page.evaluate("window.localStorage.getItem('username')")
    saved_token = page.evaluate("window.localStorage.getItem('token')")

    assert saved_username == username
    assert saved_token is not None
    assert saved_token != ""

def test_registration_with_existing_username(page: Page):
    username, password = generate_unique_user()

    # Первая успешная регистрация
    open_register_form(page)
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)
    page.locator("#registerSubmitBtn").click()

    expect(page.locator("#appSection")).to_be_visible()
    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(username)

    # Выходим, чтобы снова попасть на экран авторизации
    page.locator("#logoutBtn").click()
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()

    # Повторная регистрация с тем же логином
    page.locator('[data-auth-mode="register"]').click()
    expect(page.locator("#registerForm")).to_be_visible()

    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)
    page.locator("#registerSubmitBtn").click()

    # Проверяем inline-ошибку у поля логина
    expect(page.locator("#registerUsernameError")).to_be_visible()
    expect(page.locator("#registerUsernameError")).to_have_text("Такой логин уже существует.")

    # Проверяем, что остались на auth screen
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()

    # Проверяем, что логин-поле подсвечено как невалидное
    expect(page.locator("#registerUsername")).to_have_class("is-invalid")
    
    expect(page.locator("#registerPasswordError")).to_be_hidden()
    expect(page.locator("#registerUsername")).to_be_focused()

def test_registration_without_username(page: Page):
    open_register_form(page)

    # Заполняем только пароль
    page.locator("#registerPassword").fill("Password123")

    # Трогаем логин и уводим фокус, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerUsernameError")).to_be_visible()
    expect(page.locator("#registerUsernameError")).to_have_text("Логин обязателен.")
    expect(page.locator("#registerUsername")).to_have_class("is-invalid")

    # У пароля ошибки быть не должно
    expect(page.locator("#registerPasswordError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_without_password(page: Page):
    open_register_form(page)
    username, _ = generate_unique_user()

    # Заполняем только логин
    page.locator("#registerUsername").fill(username)

    # Трогаем логин и уводим фокус, чтобы сработала inline-валидация
    page.locator("#registerPassword").click()
    page.locator("#registerUsername").click()

    expect(page.locator("#registerPasswordError")).to_be_visible()
    expect(page.locator("#registerPasswordError")).to_have_text("Пароль обязателен.")
    expect(page.locator("#registerPassword")).to_have_class("is-invalid")

    # У логина ошибки быть не должно
    expect(page.locator("#registerUsernameError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()

def test_registration_with_spaces_in_username(page: Page):
    open_register_form(page)

    # Заполняем невалидный логин и валидный пароль
    page.locator("#registerUsername").fill("user name")
    page.locator("#registerPassword").fill("Password123")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerUsernameError")).to_be_visible()
    expect(page.locator("#registerUsernameError")).to_have_text("Логин не должен содержать пробелы.")
    expect(page.locator("#registerUsername")).to_have_class("is-invalid")

    # У пароля ошибки быть не должно
    expect(page.locator("#registerPasswordError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_with_cyrillic_in_username(page: Page):
    open_register_form(page)

    # Заполняем невалидный логин и валидный пароль
    page.locator("#registerUsername").fill("userимя")
    page.locator("#registerPassword").fill("Password123")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerUsernameError")).to_be_visible()
    expect(page.locator("#registerUsernameError")).to_have_text("Логин не должен содержать кириллицу.")
    expect(page.locator("#registerUsername")).to_have_class("is-invalid")

    # У пароля ошибки быть не должно
    expect(page.locator("#registerPasswordError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_with_username_is_too_long(page: Page):
    suffix = uuid.uuid4().hex[:29]
    username = f"uiuser_{suffix}"
    password = "Password123"
    open_register_form(page)

    # Заполняем невалидный логин и валидный пароль
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerUsernameError")).to_be_visible()
    expect(page.locator("#registerUsernameError")).to_have_text("Логин должен быть от 3 до 30 символов.")
    expect(page.locator("#registerUsername")).to_have_class("is-invalid")

    # У пароля ошибки быть не должно
    expect(page.locator("#registerPasswordError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_with_username_is_too_short(page: Page):
    open_register_form(page)

    # Заполняем невалидный логин и валидный пароль
    page.locator("#registerUsername").fill("a2")
    page.locator("#registerPassword").fill("Password123")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerUsernameError")).to_be_visible()
    expect(page.locator("#registerUsernameError")).to_have_text("Логин должен быть от 3 до 30 символов.")
    expect(page.locator("#registerUsername")).to_have_class("is-invalid")

    # У пароля ошибки быть не должно
    expect(page.locator("#registerPasswordError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_with_password_is_too_short(page: Page):
    username, _ = generate_unique_user()
    open_register_form(page)

    # Заполняем валидный логин и короткий пароль
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill("Pasw23")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerPasswordError")).to_be_visible()
    expect(page.locator("#registerPasswordError")).to_have_text("Пароль должен быть от 8 до 32 символов.")
    expect(page.locator("#registerPassword")).to_have_class("is-invalid")

    # У логина ошибки быть не должно
    expect(page.locator("#registerUsernameError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_with_password_is_too_long(page: Page):
    username, _ = generate_unique_user()
    open_register_form(page)

    # Заполняем валидный логин и короткий пароль
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill("Pasw23qwqwqw12121sqwtwrtweweqqq1233455")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerPasswordError")).to_be_visible()
    expect(page.locator("#registerPasswordError")).to_have_text("Пароль должен быть от 8 до 32 символов.")
    expect(page.locator("#registerPassword")).to_have_class("is-invalid")

    # У логина ошибки быть не должно
    expect(page.locator("#registerUsernameError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_password_with_spaces(page: Page):
    username, _ = generate_unique_user()
    open_register_form(page)

    # Заполняем валидный логин и короткий пароль
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill("Pasw23or d1 123")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerPasswordError")).to_be_visible()
    expect(page.locator("#registerPasswordError")).to_have_text("Пароль не должен содержать пробелы.")
    expect(page.locator("#registerPassword")).to_have_class("is-invalid")

    # У логина ошибки быть не должно
    expect(page.locator("#registerUsernameError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_password_with_only_digit(page: Page):
    username, _ = generate_unique_user()
    open_register_form(page)

    # Заполняем валидный логин и короткий пароль
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill("123412345678")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerPasswordError")).to_be_visible()
    expect(page.locator("#registerPasswordError")).to_have_text("Пароль должен содержать хотя бы одну латинскую букву.")
    expect(page.locator("#registerPassword")).to_have_class("is-invalid")

    # У логина ошибки быть не должно
    expect(page.locator("#registerUsernameError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_password_with_only_letеers(page: Page):
    username, _ = generate_unique_user()
    open_register_form(page)

    # Заполняем валидный логин и короткий пароль
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill("lettersletters")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerPasswordError")).to_be_visible()
    expect(page.locator("#registerPasswordError")).to_have_text("Пароль должен содержать хотя бы одну цифру.")
    expect(page.locator("#registerPassword")).to_have_class("is-invalid")

    # У логина ошибки быть не должно
    expect(page.locator("#registerUsernameError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_registration_password_with_cyrillic_letters(page: Page):
    username, _ = generate_unique_user()
    open_register_form(page)

    # Заполняем валидный логин и короткий пароль
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill("lettersкириллица")

    # Уводим фокус с логина, чтобы сработала inline-валидация
    page.locator("#registerUsername").click()
    page.locator("#registerPassword").click()

    expect(page.locator("#registerPasswordError")).to_be_visible()
    expect(page.locator("#registerPasswordError")).to_have_text("Пароль не должен содержать кириллицу.")
    expect(page.locator("#registerPassword")).to_have_class("is-invalid")

    # У логина ошибки быть не должно
    expect(page.locator("#registerUsernameError")).to_be_hidden()

    # На рабочий экран не переходим
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_switch_from_register_form_to_login_form(page: Page):
    open_register_form(page)

    # Убеждаемся, что сейчас открыта регистрация
    expect(page.locator("#registerForm")).to_be_visible()
    expect(page.locator("#loginForm")).to_be_hidden()

    # Переключаемся на окно авторизации
    page.locator('[data-auth-mode="login"]').click()

    expect(page.locator("#loginForm")).to_be_visible()
    expect(page.locator("#registerForm")).to_be_hidden()

    # Остаёмся на auth screen
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()
    
def test_theme_toggle_from_light_to_dark_and_back_preserves_register_fields(page: Page):
    open_register_form(page)

    username, _ = generate_unique_user()
    password = "Password123"

    # Заполняем поля регистрации
    page.locator("#registerUsername").fill(username)
    page.locator("#registerPassword").fill(password)

    # Переключаем тему на тёмную
    page.locator("#themeToggleBtn").click()

    expect(page.locator("body")).to_have_attribute("data-theme", "dark")
    expect(page.locator("#registerUsername")).to_have_value(username)
    expect(page.locator("#registerPassword")).to_have_value(password)

    # Переключаем тему обратно на светлую
    page.locator("#themeToggleBtn").click()

    expect(page.locator("body")).to_have_attribute("data-theme", "light")
    expect(page.locator("#registerUsername")).to_have_value(username)
    expect(page.locator("#registerPassword")).to_have_value(password)

    # Всё ещё остаёмся на экране авторизации
    expect(page.locator("#authSection")).to_be_visible()
    expect(page.locator("#appSection")).to_be_hidden()