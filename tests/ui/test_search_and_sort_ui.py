import time
import uuid
from datetime import datetime, timedelta

import requests
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5000"


def generate_unique_user():
    suffix = uuid.uuid4().hex[:6]
    return f"uiuser_{suffix}", "Password123"


def register_user_via_api(username: str, password: str):
    response = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 201


def login_user_via_api(username: str, password: str) -> str:
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def create_task_via_api(
    token: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    deadline: str | None = None,
):
    response = requests.post(
        f"{BASE_URL}/tasks",
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
    )
    assert response.status_code == 201
    return response.json()


def update_task_status_via_api(token: str, task_id: int, status: str):
    response = requests.patch(
        f"{BASE_URL}/tasks/{task_id}/status",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"status": status},
    )
    assert response.status_code == 200
    return response.json()


def open_login_form(page: Page):
    page.goto(BASE_URL)
    expect(page.locator("#loginForm")).to_be_visible()
    expect(page.locator("#registerForm")).to_be_hidden()


def login_via_ui(page: Page, username: str, password: str):
    open_login_form(page)

    page.locator("#loginUsername").fill(username)
    page.locator("#loginPassword").fill(password)
    page.locator("#loginSubmitBtn").click()

    expect(page.locator("#authSection")).to_be_hidden()
    expect(page.locator("#appSection")).to_be_visible()
    expect(page.locator("#authStatusText")).to_have_text("Авторизован")
    expect(page.locator("#userText")).to_have_text(username)


def setup_logged_in_user(page: Page):
    username, password = generate_unique_user()
    register_user_via_api(username, password)
    token = login_user_via_api(username, password)
    login_via_ui(page, username, password)
    return username, password, token


def set_select_value(page: Page, selector: str, value: str):
    page.locator(selector).evaluate(
        """(el, nextValue) => {
            el.value = nextValue;
            el.dispatchEvent(new Event("change", { bubbles: true }));
        }""",
        value,
    )


def apply_filters(
    page: Page,
    *,
    search: str | None = None,
    status: str | None = None,
    sort: str | None = None,
):
    if search is not None:
        page.locator("#searchInput").fill(search)
    if status is not None:
        set_select_value(page, "#statusFilterSelect", status)
    if sort is not None:
        set_select_value(page, "#sortSelect", sort)

    page.locator("#applyFiltersBtn").click()


def get_task_titles(page: Page) -> list[str]:
    return [text.strip() for text in page.locator("#tasksList .task-title").all_inner_texts()]


def create_search_sort_fixtures(token: str):
    now = datetime.now().replace(second=0, microsecond=0)

    task_search_title = create_task_via_api(
        token=token,
        title="Smoke login task",
        description="API regression coverage",
        priority="medium",
        deadline=(now + timedelta(days=2)).isoformat(),
    )

    task_search_description = create_task_via_api(
        token=token,
        title="Backend regression",
        description="Playwright smoke scenario in description",
        priority="low",
        deadline=(now + timedelta(days=3)).isoformat(),
    )

    task_in_progress = create_task_via_api(
        token=token,
        title="Status target task",
        description="Task that should become in progress",
        priority="medium",
        deadline=(now + timedelta(days=4)).isoformat(),
    )
    update_task_status_via_api(token, task_in_progress["id"], "in_progress")

    task_done_search = create_task_via_api(
        token=token,
        title="Smoke done task",
        description="Done status with smoke keyword",
        priority="high",
        deadline=(now + timedelta(days=1)).isoformat(),
    )
    update_task_status_via_api(token, task_done_search["id"], "done")

    task_priority_low = create_task_via_api(
        token=token,
        title="Priority low task",
        description="Priority sort fixture low",
        priority="low",
        deadline=(now + timedelta(days=6)).isoformat(),
    )

    task_priority_high = create_task_via_api(
        token=token,
        title="Priority high task",
        description="Priority sort fixture high",
        priority="high",
        deadline=(now + timedelta(days=5)).isoformat(),
    )

    task_priority_medium = create_task_via_api(
        token=token,
        title="Priority medium task",
        description="Priority sort fixture medium",
        priority="medium",
        deadline=(now + timedelta(days=7)).isoformat(),
    )

    task_deadline_late = create_task_via_api(
        token=token,
        title="Deadline late task",
        description="Later deadline fixture",
        priority="medium",
        deadline=(now + timedelta(days=10)).isoformat(),
    )

    task_deadline_soon = create_task_via_api(
        token=token,
        title="Deadline soon task",
        description="Soon deadline fixture",
        priority="medium",
        deadline=(now + timedelta(days=1, hours=2)).isoformat(),
    )

    task_created_old = create_task_via_api(
        token=token,
        title="Created old task",
        description="Created sort old",
        priority="medium",
        deadline=(now + timedelta(days=8)).isoformat(),
    )
    time.sleep(1.1)

    task_created_middle = create_task_via_api(
        token=token,
        title="Created middle task",
        description="Created sort middle",
        priority="medium",
        deadline=(now + timedelta(days=8, hours=1)).isoformat(),
    )
    time.sleep(1.1)

    task_created_new = create_task_via_api(
        token=token,
        title="Created new task",
        description="Created sort new",
        priority="medium",
        deadline=(now + timedelta(days=8, hours=2)).isoformat(),
    )

    return {
        "search_title": task_search_title,
        "search_description": task_search_description,
        "in_progress": task_in_progress,
        "done_search": task_done_search,
        "priority_low": task_priority_low,
        "priority_high": task_priority_high,
        "priority_medium": task_priority_medium,
        "deadline_late": task_deadline_late,
        "deadline_soon": task_deadline_soon,
        "created_old": task_created_old,
        "created_middle": task_created_middle,
        "created_new": task_created_new,
    }


def test_search_by_full_word_in_title(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="login")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["search_description"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Все задачи» по запросу «login».")
    expect(page.locator("#activeFilterText")).to_contain_text("поиск: login")


def test_search_by_full_word_in_description_with_enter(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    page.locator("#searchInput").fill("Playwright")
    page.locator("#searchInput").press("Enter")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_description"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Все задачи» по запросу «Playwright».")


def test_search_with_no_results_shows_empty_summary(page: Page):
    username, password, token = setup_logged_in_user(page)
    create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="no_such_task_value")

    expect(page.locator("#tasksList .task-card")).to_have_count(0)
    expect(page.locator("#tasksSummary")).to_have_text("По запросу «no_such_task_value» ничего не найдено.")
    expect(page.locator("#tasksList")).to_contain_text("Пока нет задач")


def test_filter_in_progress_shows_only_in_progress_tasks(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, status="in_progress")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["in_progress"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «В работе».")
    expect(page.locator("#activeFilterText")).to_contain_text("В работе")


def test_search_and_status_filter_work_together(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Smoke", status="done")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Готово» по запросу «Smoke».")
    expect(page.locator("#activeFilterText")).to_contain_text("Готово")
    expect(page.locator("#activeFilterText")).to_contain_text("поиск: Smoke")


def test_sort_by_priority_desc_orders_high_medium_low(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Priority", sort="priority_desc")

    expect(page.locator("#tasksList .task-title")).to_have_count(3)
    titles = get_task_titles(page)

    assert titles == [
        fixtures["priority_high"]["title"],
        fixtures["priority_medium"]["title"],
        fixtures["priority_low"]["title"],
    ]


def test_sort_by_created_desc_orders_newest_first(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Created sort", sort="created_desc")

    expect(page.locator("#tasksList .task-title")).to_have_count(3)
    titles = get_task_titles(page)

    assert titles == [
        fixtures["created_new"]["title"],
        fixtures["created_middle"]["title"],
        fixtures["created_old"]["title"],
    ]


def test_reset_filters_restores_default_controls_and_hides_active_filter_chips(page: Page):
    username, password, token = setup_logged_in_user(page)
    create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Smoke", status="done", sort="created_desc")

    expect(page.locator("#activeFilterChips")).to_be_visible()

    page.locator("#resetFiltersBtn").click()

    expect(page.locator("#searchInput")).to_have_value("")
    expect(page.locator("#statusFilterSelect")).to_have_value("all")
    expect(page.locator("#sortSelect")).to_have_value("deadline_asc")
    expect(page.locator("#activeFilterChips")).to_be_hidden()
    expect(page.locator("#activeFilterText")).to_have_text("Все задачи • сортировка: Ближайший дедлайн")


def test_removing_only_search_filter_chip_keeps_status_filter(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Smoke", status="done")

    expect(page.locator("#activeFilterChips")).to_be_visible()
    page.locator('[data-clear-filter="search"]').click()

    expect(page.locator("#searchInput")).to_have_value("")
    expect(page.locator("#statusFilterSelect")).to_have_value("done")
    expect(page.locator("#tasksList")).to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Готово».")
    
def test_search_by_partial_word(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="ogin")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["search_description"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Все задачи» по запросу «ogin».")
    
def test_search_is_case_insensitive(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="SMOKE")

    expect(page.locator("#tasksList .task-card")).to_have_count(3)
    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_description"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(fixtures["done_search"]["title"])
    
def test_empty_search_shows_tasks_without_search_limitation(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="login")
    apply_filters(page, search="")

    expect(page.locator("#searchInput")).to_have_value("")
    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_description"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(fixtures["in_progress"]["title"])
    expect(page.locator("#activeFilterText")).not_to_contain_text("поиск:")
    
def test_search_with_spaces_around_value_is_trimmed(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="   login   ")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["search_description"]["title"])
    expect(page.locator("#activeFilterText")).to_contain_text("поиск: login")
    
def test_filter_all_tasks_shows_tasks_of_all_statuses(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, status="all")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(fixtures["in_progress"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#statusFilterSelect")).to_have_value("all")
    
def test_filter_new_shows_only_new_tasks(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, status="new")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["in_progress"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#tasksSummary")).to_contain_text("в выборке «Новые».")
    
def test_filter_done_shows_only_done_tasks(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, status="done")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["in_progress"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Готово».")
    
def test_switching_between_status_filters_updates_list_correctly(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, status="done")
    expect(page.locator("#tasksList")).to_contain_text(fixtures["done_search"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["in_progress"]["title"])

    apply_filters(page, status="new")
    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["done_search"]["title"])

    apply_filters(page, status="in_progress")
    expect(page.locator("#tasksList")).to_contain_text(fixtures["in_progress"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(fixtures["done_search"]["title"])
    
def test_search_matches_but_status_does_not_match_returns_no_results(page: Page):
    username, password, token = setup_logged_in_user(page)
    create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="login", status="done")

    expect(page.locator("#tasksList .task-card")).to_have_count(0)
    expect(page.locator("#tasksSummary")).to_have_text("По запросу «login» ничего не найдено.")
    
def test_status_matches_but_search_does_not_match_returns_no_results(page: Page):
    username, password, token = setup_logged_in_user(page)
    create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="no_match_value", status="in_progress")

    expect(page.locator("#tasksList .task-card")).to_have_count(0)
    expect(page.locator("#tasksSummary")).to_have_text("По запросу «no_match_value» ничего не найдено.")
    
def test_sort_by_deadline_asc_orders_nearest_deadline_first(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Deadline", sort="deadline_asc")

    expect(page.locator("#tasksList .task-title")).to_have_count(2)
    titles = get_task_titles(page)

    assert titles == [
        fixtures["deadline_soon"]["title"],
        fixtures["deadline_late"]["title"],
    ]
    
def test_changing_sort_with_existing_search_and_status_keeps_filters(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Priority sort fixture", status="new", sort="priority_desc")

    titles = get_task_titles(page)
    assert titles == [
        fixtures["priority_high"]["title"],
        fixtures["priority_medium"]["title"],
        fixtures["priority_low"]["title"],
    ]

    apply_filters(page, sort="created_desc")

    expect(page.locator("#searchInput")).to_have_value("Priority sort fixture")
    expect(page.locator("#statusFilterSelect")).to_have_value("new")
    expect(page.locator("#sortSelect")).to_have_value("created_desc")
    expect(page.locator("#activeFilterText")).to_contain_text("Новые")
    expect(page.locator("#activeFilterText")).to_contain_text("поиск: Priority sort fixture")
    expect(page.locator("#activeFilterText")).to_contain_text("Сначала новые")

    titles = get_task_titles(page)
    assert titles == [
        fixtures["priority_medium"]["title"],
        fixtures["priority_high"]["title"],
        fixtures["priority_low"]["title"],
    ]
    
def test_removing_only_status_filter_chip_keeps_search_and_sort(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Smoke", status="done", sort="created_desc")

    expect(page.locator("#activeFilterChips")).to_be_visible()
    page.locator('[data-clear-filter="status"]').click()

    expect(page.locator("#searchInput")).to_have_value("Smoke")
    expect(page.locator("#statusFilterSelect")).to_have_value("all")
    expect(page.locator("#sortSelect")).to_have_value("created_desc")

    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_description"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(fixtures["done_search"]["title"])
    
def test_removing_only_sort_filter_chip_keeps_other_filters(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="Priority sort fixture", status="new", sort="priority_desc")

    titles = get_task_titles(page)
    assert titles == [
        fixtures["priority_high"]["title"],
        fixtures["priority_medium"]["title"],
        fixtures["priority_low"]["title"],
    ]

    page.locator('[data-clear-filter="sort"]').click()

    expect(page.locator("#searchInput")).to_have_value("Priority sort fixture")
    expect(page.locator("#statusFilterSelect")).to_have_value("new")
    expect(page.locator("#sortSelect")).to_have_value("deadline_asc")

    titles = get_task_titles(page)
    assert titles == [
        fixtures["priority_high"]["title"],
        fixtures["priority_low"]["title"],
        fixtures["priority_medium"]["title"],
    ]

def test_summary_for_non_empty_selection(page: Page):
    username, password, token = setup_logged_in_user(page)
    fixtures = create_search_sort_fixtures(token)

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, search="login")

    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Все задачи» по запросу «login».")
    expect(page.locator("#tasksList")).to_contain_text(fixtures["search_title"]["title"])
    
def test_summary_for_empty_selection_without_search(page: Page):
    username, password, token = setup_logged_in_user(page)

    only_new_task = create_task_via_api(
        token=token,
        title="Only new task",
        description="No done tasks here",
        priority="medium",
    )

    page.goto(BASE_URL)
    expect(page.locator("#appSection")).to_be_visible()

    apply_filters(page, status="done")

    expect(page.locator("#tasksList .task-card")).to_have_count(0)
    expect(page.locator("#tasksSummary")).to_have_text("Сейчас нет задач в выборке «Готово».")