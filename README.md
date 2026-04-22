# Todo QA

Учебный pet-project для практики ручного тестирования, API-автотестов и UI-автотестов.

Проект представляет собой одно Flask-приложение с backend и встроенным UI. Пользователь может зарегистрироваться, войти в систему, работать только со своими задачами, искать их, фильтровать по статусу, редактировать, менять статус, удалять и управлять дедлайном.

---

## Что это за проект

`Todo QA` — это учебное приложение для управления личными задачами.

Цель проекта:
- отработать backend-логику на Flask;
- потренироваться в API-тестировании на `pytest + requests`;
- покрыть пользовательские сценарии UI-автотестами на Playwright;
- поддерживать документацию, код и тесты в синхронном состоянии.

Функциональность проекта:
- регистрация и логин;
- JWT access token;
- список задач пользователя;
- получение задачи по id;
- создание задачи;
- полное редактирование задачи;
- отдельный endpoint смены статуса;
- удаление задачи;
- поиск по задачам;
- фильтр по статусу;
- дедлайн;
- интерфейс с отдельным экраном авторизации и отдельной рабочей зоной.

---

## Стек

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Flask-JWT-Extended
- Werkzeug security
- python-dotenv

### Frontend
- HTML
- CSS
- JavaScript

### Тестирование

#### API
- pytest
- requests

#### UI
- Playwright
- pytest-playwright

---

## Архитектура проекта

Проект реализован как **одно Flask-приложение**:
- backend и UI находятся в одном проекте;
- HTML-шаблон рендерится через Flask;
- клиентская логика лежит в `app.js`;
- стили лежат в `styles.css`.

### Основные файлы

```text
TO-DO_APP/
├── app/
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   ├── templates/
│   │   └── index.html
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   └── tasks.py
│
├── tests/
│   ├── api/
│   │   ├── test_register.py
│   │   ├── test_login.py
│   │   ├── test_tasks_get.py
│   │   ├── test_task_get_by_id.py
│   │   ├── test_tasks_create.py
│   │   ├── test_task_update.py
│   │   ├── test_tasks_status.py
│   │   └── test_tasks_delete.py
│   ├── ui/
│   │   ├── test_register_ui.py
│   │   ├── test_login_ui.py
│   │   ├── test_create_task_ui.py
│   │   ├── test_edit_task_ui.py
│   │   ├── test_edit_task_status_ui.py
│   │   ├── test_delete_task_ui.py
│   │   └── test_search_and_sort_ui.py
│   └── README.txt
│
├── conftest.py
├── pytest.ini
├── requirements.txt
├── run.py
├── README.md
├── .env
└── .env.example
```

---

## Возможности проекта

### Авторизация
- регистрация нового пользователя;
- логин по username/password;
- выдача JWT access token;
- logout на клиенте;
- хранение токена и username в `localStorage`.

### Tasks API
- `GET /tasks` — получить список своих задач;
- `GET /tasks/<id>` — получить одну свою задачу;
- `POST /tasks` — создать задачу;
- `PATCH /tasks/<id>` — обновить title / description / priority / deadline;
- `PATCH /tasks/<id>/status` — изменить только статус;
- `DELETE /tasks/<id>` — удалить задачу.

### Расширения API
- поиск по `title` и `description`;
- фильтр по `status`;
- поддержка `deadline`;
- защита от доступа к чужим задачам.

### UI
- отдельный экран авторизации;
- отдельная рабочая зона;
- статистика по задачам;
- поиск;
- фильтр по статусу;
- client-side сортировка;
- создание задачи;
- редактирование задачи в modal;
- удаление с подтверждением в modal;
- theme toggle;
- inline-валидация полей;
- автологаут при истечении токена.

---

## Модель данных

### User
- `id`
- `username`
- `password_hash`
- `created_at`

### Task
- `id`
- `user_id`
- `title`
- `description`
- `status`
- `priority`
- `deadline`
- `created_at`

### Формат задачи в API

```json
{
  "id": 1,
  "title": "Проверить API логина",
  "description": "Проверить позитивные и негативные сценарии",
  "status": "new",
  "priority": "high",
  "deadline": "2026-12-12T18:30:00Z",
  "created_at": "2026-04-10T10:30:00Z"
}
```

---

## Валидации

### Username
- обязателен;
- не может быть пустым или состоять только из пробелов;
- не может содержать whitespace;
- длина: от 3 до 30 символов;
- не может содержать кириллицу;
- не может состоять только из цифр;
- должен быть уникальным при регистрации.

### Password
- обязателен;
- не может содержать whitespace;
- длина: от 8 до 32 символов;
- не может содержать кириллицу;
- должен содержать хотя бы одну латинскую букву;
- должен содержать хотя бы одну цифру.

### Title
- обязателен при создании;
- при update валидируется, если передан;
- после `trim()` не может быть пустым;
- длина: от 1 до 80 символов.

### Description
- необязателен;
- может быть пустой строкой;
- максимум 500 символов.

### Priority
- допустимые значения:
  - `low`
  - `medium`
  - `high`
- если не передан или передан как `null` в create, используется `medium`.

### Status
- допустимые значения:
  - `new`
  - `in_progress`
  - `done`

### Deadline
- необязателен;
- может быть `null`;
- должен быть валидным ISO datetime;
- должен быть минимум на 30 минут позже текущего времени;
- в update `null` удаляет дедлайн.

---

## Бизнес-правила

- каждый пользователь работает только со своими задачами;
- доступ к задачам другого пользователя запрещён;
- при создании `status` всегда устанавливается в `new`;
- при создании `priority` по умолчанию устанавливается в `medium`;
- если `deadline` не передан, задача создаётся без дедлайна;
- `GET /tasks` возвращает только задачи текущего пользователя;
- поиск выполняется только по задачам текущего пользователя;
- поиск работает по `title` и `description`;
- поиск на сервере — без учёта регистра;
- сервер возвращает список задач в порядке `created_at DESC`;
- дополнительная сортировка в UI выполняется на клиенте;
- поля `id`, `user_id`, `created_at`, `status` не должны управляться клиентом через create/update;
- пароли не хранятся в открытом виде.

---

## API

### `POST /register`
Регистрация нового пользователя.

#### Request
```json
{
  "username": "tester1",
  "password": "Password123"
}
```

#### Success
- `201 Created`

```json
{
  "message": "User created successfully"
}
```

#### Errors
- `400 Bad Request`
- `409 Conflict`

---

### `POST /login`
Логин и выдача access token.

#### Request
```json
{
  "username": "tester1",
  "password": "Password123"
}
```

#### Success
- `200 OK`

```json
{
  "access_token": "jwt-token"
}
```

#### Errors
- `400 Bad Request`
- `401 Unauthorized`

---

### `GET /tasks`
Получить список задач текущего пользователя.

#### Query params
- `status`
- `search`

#### Success
- `200 OK`

#### Errors
- `400 Bad Request`
- `401 Unauthorized`
- `422 Unprocessable Entity`

---

### `GET /tasks/<id>`
Получить одну задачу текущего пользователя по id.

#### Success
- `200 OK`

#### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `422 Unprocessable Entity`

---

### `POST /tasks`
Создать новую задачу.

#### Request
```json
{
  "title": "Проверить сортировку задач",
  "description": "Проверить client-side сортировку по deadline",
  "priority": "high",
  "deadline": "2026-12-12T18:30:00Z"
}
```

#### Success
- `201 Created`

#### Errors
- `400 Bad Request`
- `401 Unauthorized`
- `422 Unprocessable Entity`

---

### `PATCH /tasks/<id>`
Обновить `title`, `description`, `priority` и/или `deadline`.

#### Request
```json
{
  "title": "Обновлённый заголовок",
  "description": "Обновлённое описание",
  "priority": "medium",
  "deadline": null
}
```

#### Success
- `200 OK`

#### Errors
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `422 Unprocessable Entity`

---

### `PATCH /tasks/<id>/status`
Изменить только статус задачи.

#### Request
```json
{
  "status": "done"
}
```

#### Success
- `200 OK`

#### Errors
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `422 Unprocessable Entity`

---

### `DELETE /tasks/<id>`
Удалить задачу.

#### Success
- `204 No Content`

#### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `422 Unprocessable Entity`

---

## Формат ошибок

Для бизнес-ошибок и серверной валидации используется такой формат:

```json
{
  "message": "Title is required"
}
```

Для части ошибок, которые генерирует JWT middleware, используется другой формат:

```json
{
  "msg": "Missing Authorization Header"
}
```

Это нормальное поведение текущей реализации.

---

## Локальный запуск

### 1. Клонировать проект
```bash
git clone <your-repo-url>
cd <your-project-folder>
```

### 2. Создать и активировать виртуальное окружение

#### Windows (PowerShell)
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Подготовить PostgreSQL
Создай базу данных, например:

```sql
CREATE DATABASE todo_db;
```

### 5. Создать `.env`
В корне проекта создай файл `.env`:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/todo_db
```

> При желании можно использовать свои значения для логина, пароля и имени базы.

### 6. Запустить приложение
```bash
python run.py
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:5000
```

---

## Запуск тестов

### API-тесты
```bash
pytest tests/api -v
```

### UI-тесты

Зависимости для UI уже входят в `requirements.txt`, но для первого запуска нужно отдельно скачать браузеры Playwright:

```bash
playwright install
```

После этого можно запускать UI-тесты:

```bash
pytest tests/ui -v
```

### Все тесты сразу
```bash
pytest -v
```

---

## Что уже покрыто тестами

### API
- register: позитивные и негативные сценарии;
- login: успешный вход, невалидные данные, неверные учётные данные;
- `GET /tasks`: свои задачи, пустой список, отсутствие токена, невалидный токен, поиск, фильтр;
- `GET /tasks/<id>`: своя задача, чужая задача, несуществующая задача;
- `POST /tasks`: обязательные поля, длины, priority, deadline, auth edge cases, extra fields;
- `PATCH /tasks/<id>`: частичное обновление, валидации, deadline, access checks;
- `PATCH /tasks/<id>/status`: валидные/невалидные статусы, access checks;
- `DELETE /tasks/<id>`: успешное удаление, повторное удаление, access checks.

### UI
- регистрация;
- логин;
- создание задачи;
- редактирование задачи;
- смена статуса;
- удаление задачи;
- поиск и сортировка;
- theme toggle;
- сценарии с истёкшим токеном и автологаутом.

---

## Особенности UI

В интерфейсе реализованы:
- отдельный экран авторизации;
- отдельная рабочая зона;
- статистика по задачам;
- поиск;
- фильтр по статусу;
- сортировка:
  - ближайший дедлайн,
  - высокий приоритет,
  - сначала новые;
- форма создания задачи;
- модальное окно редактирования;
- модальное окно подтверждения удаления;
- theme toggle;
- inline-валидация;
- сохранение `token`, `username`, `theme`, `sortBy` в `localStorage`.

---

## Что не входит в проект

В проект не входят:
- refresh token;
- профиль пользователя;
- смена пароля;
- совместная работа над задачами;
- комментарии и вложения;
- пагинация;
- серверная сортировка;
- расширенная аналитика.

---

## Автор

Учебный pet-project для практики QA и автотестов.

Основной фокус проекта:
- понимание backend-валидаций;
- построение тестового покрытия по endpoint’ам;
- переход от API-автотестов к UI-автотестам на реальном приложении.
