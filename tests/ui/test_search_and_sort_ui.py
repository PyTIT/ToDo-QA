import time
from datetime import datetime, timedelta

import pytest
from playwright.sync_api import expect

from conftest import create_task_via_api, update_task_status_via_api


def apply_filters(page, set_select_value, *, search=None, status=None, sort=None):
    if search is not None:
        page.locator("#searchInput").fill(search)
    if status is not None:
        set_select_value(page, "#statusFilterSelect", status)
    if sort is not None:
        set_select_value(page, "#sortSelect", sort)
    page.locator("#applyFiltersBtn").click()


def get_task_titles(page):
    return [text.strip() for text in page.locator("#tasksList .task-title").all_inner_texts()]


@pytest.fixture
def search_sort_page(page, api_user, base_url, login_via_ui):
    login_via_ui(page, api_user.username, api_user.password)
    page.goto(base_url)
    expect(page.locator("#appSection")).to_be_visible()
    return page, api_user.token


@pytest.fixture
def search_sort_fixtures(search_sort_page, base_url):
    page, token = search_sort_page
    now = datetime.now().replace(second=0, microsecond=0)

    def create(title, description="", priority="medium", deadline=None, status=None):
        task = create_task_via_api(
            token,
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            base_url=base_url,
        ).json()
        if status:
            update_task_status_via_api(token, task["id"], status, base_url=base_url)
        return task

    fixtures = {
        "search_title": create(
            "Smoke login task",
            "API regression coverage",
            deadline=(now + timedelta(days=2)).isoformat(),
        ),
        "search_description": create(
            "Backend regression",
            "Playwright smoke scenario in description",
            priority="low",
            deadline=(now + timedelta(days=3)).isoformat(),
        ),
        "in_progress": create(
            "Status target task",
            "Task that should become in progress",
            deadline=(now + timedelta(days=4)).isoformat(),
            status="in_progress",
        ),
        "done_search": create(
            "Smoke done task",
            "Done status with smoke keyword",
            priority="high",
            deadline=(now + timedelta(days=1)).isoformat(),
            status="done",
        ),
        "priority_low": create(
            "Priority low task",
            "Priority sort fixture low",
            priority="low",
            deadline=(now + timedelta(days=6)).isoformat(),
        ),
        "priority_high": create(
            "Priority high task",
            "Priority sort fixture high",
            priority="high",
            deadline=(now + timedelta(days=5)).isoformat(),
        ),
        "priority_medium": create(
            "Priority medium task",
            "Priority sort fixture medium",
            priority="medium",
            deadline=(now + timedelta(days=7)).isoformat(),
        ),
        "deadline_late": create(
            "Deadline late task",
            "Later deadline fixture",
            deadline=(now + timedelta(days=10)).isoformat(),
        ),
        "deadline_soon": create(
            "Deadline soon task",
            "Soon deadline fixture",
            deadline=(now + timedelta(days=1, hours=2)).isoformat(),
        ),
    }

    fixtures["created_old"] = create(
        "Created old task",
        "Created sort old",
        deadline=(now + timedelta(days=8)).isoformat(),
    )
    time.sleep(1.1)
    fixtures["created_middle"] = create(
        "Created middle task",
        "Created sort middle",
        deadline=(now + timedelta(days=8, hours=1)).isoformat(),
    )
    time.sleep(1.1)
    fixtures["created_new"] = create(
        "Created new task",
        "Created sort new",
        deadline=(now + timedelta(days=8, hours=2)).isoformat(),
    )

    return fixtures


@pytest.mark.parametrize(
    ("search", "expected_count", "must_have", "must_not_have", "summary"),
    [
        ("login", 1, ["search_title"], ["search_description", "done_search"], "1 задача в выборке «Все задачи» по запросу «login»."),
        ("ogin", 1, ["search_title"], ["search_description", "done_search"], "1 задача в выборке «Все задачи» по запросу «ogin»."),
        ("SMOKE", 3, ["search_title", "search_description", "done_search"], [], None),
        ("no_such_task_value", 0, [], [], "По запросу «no_such_task_value» ничего не найдено."),
    ],
)
def test_search_variants(page, set_select_value, search_sort_page, search_sort_fixtures, search, expected_count, must_have, must_not_have, summary):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, search=search)

    expect(page.locator("#tasksList .task-card")).to_have_count(expected_count)

    for key in must_have:
        expect(page.locator("#tasksList")).to_contain_text(search_sort_fixtures[key]["title"])
    for key in must_not_have:
        expect(page.locator("#tasksList")).not_to_contain_text(search_sort_fixtures[key]["title"])
    if summary:
        expect(page.locator("#tasksSummary")).to_have_text(summary)


def test_search_by_full_word_in_description_with_enter(search_sort_page, search_sort_fixtures):
    page, _ = search_sort_page

    page.locator("#searchInput").fill("Playwright")
    page.locator("#searchInput").press("Enter")

    expect(page.locator("#tasksList")).to_contain_text(search_sort_fixtures["search_description"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(search_sort_fixtures["search_title"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Все задачи» по запросу «Playwright».")


@pytest.mark.parametrize(
    ("status", "must_have", "must_not_have", "summary"),
    [
        ("all", ["search_title", "in_progress", "done_search"], [], None),
        ("new", ["search_title"], ["in_progress", "done_search"], "в выборке «Новые»."),
        ("in_progress", ["in_progress"], ["done_search"], "1 задача в выборке «В работе»."),
        ("done", ["done_search"], ["search_title", "in_progress"], "1 задача в выборке «Готово»."),
    ],
)
def test_status_filters(page, set_select_value, search_sort_page, search_sort_fixtures, status, must_have, must_not_have, summary):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, status=status)

    for key in must_have:
        expect(page.locator("#tasksList")).to_contain_text(search_sort_fixtures[key]["title"])
    for key in must_not_have:
        expect(page.locator("#tasksList")).not_to_contain_text(search_sort_fixtures[key]["title"])
    if summary:
        expect(page.locator("#tasksSummary")).to_contain_text(summary)


def test_search_and_status_filter_work_together(page, set_select_value, search_sort_page, search_sort_fixtures):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, search="Smoke", status="done")

    expect(page.locator("#tasksList")).to_contain_text(search_sort_fixtures["done_search"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(search_sort_fixtures["search_title"]["title"])
    expect(page.locator("#tasksSummary")).to_have_text("1 задача в выборке «Готово» по запросу «Smoke».")
    expect(page.locator("#activeFilterText")).to_contain_text("Готово")
    expect(page.locator("#activeFilterText")).to_contain_text("поиск: Smoke")


def test_search_value_is_trimmed(page, set_select_value, search_sort_page, search_sort_fixtures):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, search="   login   ")

    expect(page.locator("#tasksList")).to_contain_text(search_sort_fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).not_to_contain_text(search_sort_fixtures["search_description"]["title"])
    expect(page.locator("#activeFilterText")).to_contain_text("поиск: login")


@pytest.mark.parametrize(
    ("search", "status", "summary"),
    [
        ("login", "done", "По запросу «login» ничего не найдено."),
        ("no_match_value", "in_progress", "По запросу «no_match_value» ничего не найдено."),
    ],
)
def test_search_and_status_mismatch_returns_empty(page, set_select_value, search_sort_page, search_sort_fixtures, search, status, summary):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, search=search, status=status)

    expect(page.locator("#tasksList .task-card")).to_have_count(0)
    expect(page.locator("#tasksSummary")).to_have_text(summary)


@pytest.mark.parametrize(
    ("search", "sort", "expected_keys"),
    [
        ("Priority", "priority_desc", ["priority_high", "priority_medium", "priority_low"]),
        ("Created sort", "created_desc", ["created_new", "created_middle", "created_old"]),
        ("Deadline", "deadline_asc", ["deadline_soon", "deadline_late"]),
    ],
)
def test_sort_orders(page, set_select_value, search_sort_page, search_sort_fixtures, search, sort, expected_keys):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, search=search, sort=sort)

    expect(page.locator("#tasksList .task-title")).to_have_count(len(expected_keys))
    assert get_task_titles(page) == [search_sort_fixtures[key]["title"] for key in expected_keys]


def test_reset_filters_restores_defaults(page, set_select_value, search_sort_page, search_sort_fixtures):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, search="Smoke", status="done", sort="created_desc")

    expect(page.locator("#activeFilterChips")).to_be_visible()
    page.locator("#resetFiltersBtn").click()

    expect(page.locator("#searchInput")).to_have_value("")
    expect(page.locator("#statusFilterSelect")).to_have_value("all")
    expect(page.locator("#sortSelect")).to_have_value("deadline_asc")
    expect(page.locator("#activeFilterChips")).to_be_hidden()
    expect(page.locator("#activeFilterText")).to_have_text("Все задачи • сортировка: Ближайший дедлайн")


@pytest.mark.parametrize(
    ("chip_key", "search", "status", "sort"),
    [
        ("search", "Smoke", "done", None),
        ("status", "Smoke", "done", "created_desc"),
        ("sort", "Priority sort fixture", "new", "priority_desc"),
    ],
)
def test_filter_chips_clear_only_target_filter(page, set_select_value, search_sort_page, search_sort_fixtures, chip_key, search, status, sort):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, search=search, status=status, sort=sort)

    page.locator(f'[data-clear-filter="{chip_key}"]').click()

    if chip_key == "search":
        expect(page.locator("#searchInput")).to_have_value("")
        expect(page.locator("#statusFilterSelect")).to_have_value("done")
    elif chip_key == "status":
        expect(page.locator("#searchInput")).to_have_value("Smoke")
        expect(page.locator("#statusFilterSelect")).to_have_value("all")
        expect(page.locator("#sortSelect")).to_have_value("created_desc")
    else:
        expect(page.locator("#searchInput")).to_have_value("Priority sort fixture")
        expect(page.locator("#statusFilterSelect")).to_have_value("new")
        expect(page.locator("#sortSelect")).to_have_value("deadline_asc")


def test_empty_search_after_non_empty_search_restores_full_selection(page, set_select_value, search_sort_page, search_sort_fixtures):
    page, _ = search_sort_page
    apply_filters(page, set_select_value, search="login")
    apply_filters(page, set_select_value, search="")

    expect(page.locator("#searchInput")).to_have_value("")
    expect(page.locator("#tasksList")).to_contain_text(search_sort_fixtures["search_title"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(search_sort_fixtures["search_description"]["title"])
    expect(page.locator("#tasksList")).to_contain_text(search_sort_fixtures["in_progress"]["title"])
    expect(page.locator("#activeFilterText")).not_to_contain_text("поиск:")


def test_summary_for_empty_selection_without_search(page, set_select_value, search_sort_page, base_url):
    page, token = search_sort_page
    create_task_via_api(
        token,
        title="Only new task",
        description="No done tasks here",
        priority="medium",
        deadline=None,
        base_url=base_url,
    )

    apply_filters(page, set_select_value, status="done")

    expect(page.locator("#tasksList .task-card")).to_have_count(0)
    expect(page.locator("#tasksSummary")).to_have_text("Сейчас нет задач в выборке «Готово».")
