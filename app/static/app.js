const API_BASE = "";

const state = {
  token: localStorage.getItem("token") || "",
  username: localStorage.getItem("username") || "",
  tasks: [],
  filter: "all",
  authMode: "login",
};

const elements = {
  authSection: document.getElementById("authSection"),
  appSection: document.getElementById("appSection"),
  messageBox: document.getElementById("messageBox"),
  userText: document.getElementById("userText"),
  authStatusText: document.getElementById("authStatusText"),
  totalCount: document.getElementById("totalCount"),
  newCount: document.getElementById("newCount"),
  progressCount: document.getElementById("progressCount"),
  doneCount: document.getElementById("doneCount"),
  tasksList: document.getElementById("tasksList"),
  logoutBtn: document.getElementById("logoutBtn"),
  reloadTasksBtn: document.getElementById("reloadTasksBtn"),
  loginForm: document.getElementById("loginForm"),
  registerForm: document.getElementById("registerForm"),
  taskForm: document.getElementById("taskForm"),
  authModeTriggers: document.querySelectorAll("[data-auth-mode]"),
  authForms: document.querySelectorAll("[data-form-mode]"),
};

elements.loginForm?.addEventListener("submit", loginUser);
elements.registerForm?.addEventListener("submit", registerUser);
elements.taskForm?.addEventListener("submit", createTask);
elements.reloadTasksBtn?.addEventListener("click", () => loadTasks());
elements.logoutBtn?.addEventListener("click", logout);
elements.tasksList?.addEventListener("click", handleTaskAction);

elements.authModeTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => {
    const nextMode = trigger.dataset.authMode;
    if (!nextMode) return;
    setAuthMode(nextMode);
  });
});

document.querySelectorAll("[data-filter]").forEach((button) => {
  button.addEventListener("click", () => {
    state.filter = button.dataset.filter || "all";
    updateFilterButtons();
    renderTasks();
  });
});

function showMessage(text, kind = "info") {
  if (!elements.messageBox) return;
  elements.messageBox.textContent = text;
  elements.messageBox.classList.remove("hidden", "is-error", "is-success", "is-warning");
  if (kind === "error") {
    elements.messageBox.classList.add("is-error");
  } else if (kind === "success") {
    elements.messageBox.classList.add("is-success");
  } else if (kind === "warning") {
    elements.messageBox.classList.add("is-warning");
  }
}

function clearMessage() {
  if (!elements.messageBox) return;
  elements.messageBox.textContent = "";
  elements.messageBox.classList.add("hidden");
  elements.messageBox.classList.remove("is-error", "is-success", "is-warning");
}

function safeSetText(node, value) {
  if (node) {
    node.textContent = value;
  }
}

function setAuthMode(mode) {
  if (mode !== "login" && mode !== "register") return;
  state.authMode = mode;
  updateAuthMode();
}

function updateAuthMode() {
  elements.authForms.forEach((form) => {
    form.classList.toggle("hidden", form.dataset.formMode !== state.authMode);
  });

  elements.authModeTriggers.forEach((trigger) => {
    const isActive = trigger.dataset.authMode === state.authMode;
    trigger.classList.toggle("is-active", isActive);
    trigger.setAttribute("aria-pressed", isActive ? "true" : "false");
  });

  document.querySelectorAll("[data-auth-copy]").forEach((block) => {
    block.classList.toggle("hidden", block.dataset.authCopy !== state.authMode);
  });
}

function updateFilterButtons() {
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.filter === state.filter);
  });
}

function updateStats() {
  const total = state.tasks.length;
  const totalNew = state.tasks.filter((task) => normalizeStatus(task.status) === "new").length;
  const totalInProgress = state.tasks.filter((task) => normalizeStatus(task.status) === "in_progress").length;
  const totalDone = state.tasks.filter((task) => normalizeStatus(task.status) === "done").length;

  safeSetText(elements.totalCount, String(total));
  safeSetText(elements.newCount, String(totalNew));
  safeSetText(elements.progressCount, String(totalInProgress));
  safeSetText(elements.doneCount, String(totalDone));
}

function updateView() {
  const isAuthorized = Boolean(state.token);

  safeSetText(elements.userText, state.username || "—");
  safeSetText(elements.authStatusText, isAuthorized ? "Авторизован" : "Не авторизован");

  elements.logoutBtn?.classList.toggle("hidden", !isAuthorized);
  elements.authSection?.classList.toggle("hidden", isAuthorized);
  elements.appSection?.classList.toggle("hidden", !isAuthorized);

  if (isAuthorized) {
    loadTasks();
  } else {
    state.tasks = [];
    updateStats();
    renderTasks();
  }

  updateFilterButtons();
  updateAuthMode();
}

async function safeReadJson(response) {
  try {
    return await response.json();
  } catch (_error) {
    return {};
  }
}

function getAuthHeaders(withJson = false) {
  const headers = {};
  if (withJson) {
    headers["Content-Type"] = "application/json";
  }
  if (state.token) {
    headers["Authorization"] = `Bearer ${state.token}`;
  }
  return headers;
}

async function registerUser(event) {
  event.preventDefault();
  clearMessage();

  const username = document.getElementById("registerUsername")?.value.trim() || "";
  const password = document.getElementById("registerPassword")?.value.trim() || "";

  try {
    const response = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify({ username, password }),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      showMessage(data.error || data.message || "Не удалось зарегистрироваться.", "error");
      return;
    }

    elements.registerForm?.reset();
    const loginField = document.getElementById("loginUsername");
    if (loginField) {
      loginField.value = username;
    }

    setAuthMode("login");
    showMessage("Аккаунт создан. Теперь войди в систему.", "success");
  } catch (_error) {
    showMessage("Сервис регистрации недоступен.", "error");
  }
}

async function loginUser(event) {
  event.preventDefault();
  clearMessage();

  const username = document.getElementById("loginUsername")?.value.trim() || "";
  const password = document.getElementById("loginPassword")?.value.trim() || "";

  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify({ username, password }),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      showMessage(data.error || data.message || "Не удалось войти.", "error");
      return;
    }

    state.token = data.access_token || "";
    state.username = username;

    localStorage.setItem("token", state.token);
    localStorage.setItem("username", state.username);

    elements.loginForm?.reset();
    showMessage("Вход выполнен успешно.", "success");
    updateView();
    loadTasks({ preserveMessage: true });
  } catch (_error) {
    showMessage("Сервис входа недоступен.", "error");
  }
}

async function loadTasks(options = {}) {
  const { preserveMessage = false } = options;
  if (!preserveMessage) {
    clearMessage();
  }

  try {
    const response = await fetch(`${API_BASE}/tasks`, {
      method: "GET",
      headers: getAuthHeaders(false),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      showMessage(data.error || data.message || "Не удалось загрузить задачи.", "error");
      return;
    }

    state.tasks = Array.isArray(data) ? sortTasks(data) : [];
    updateStats();
    renderTasks();
  } catch (_error) {
    state.tasks = [];
    updateStats();
    renderTasks();
    showMessage("Tasks API пока не готов. Интерфейс уже подготовлен под подключение.", "warning");
  }
}

function sortTasks(tasks) {
  return [...tasks].sort((first, second) => {
    const firstDate = first?.created_at ? new Date(first.created_at).getTime() : 0;
    const secondDate = second?.created_at ? new Date(second.created_at).getTime() : 0;
    return secondDate - firstDate;
  });
}

function renderTasks() {
  if (!elements.tasksList) return;

  const filteredTasks = state.filter === "all"
    ? state.tasks
    : state.tasks.filter((task) => normalizeStatus(task.status) === state.filter);

  if (!filteredTasks.length) {
    elements.tasksList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state__icon">⌁</div>
        <div class="empty-state__title">Пока нет задач</div>
        <div class="empty-state__text">Создай первую задачу или выбери другой фильтр.</div>
      </div>
    `;
    return;
  }

  elements.tasksList.innerHTML = filteredTasks.map((task) => {
    const status = normalizeStatus(task.status);
    const priority = normalizePriority(task.priority);

    return `
      <article class="task-card" data-task-id="${task.id}">
        <div class="task-card__header">
          <div class="task-card__identity">
            <div class="task-card__kicker">Задача #${task.id ?? "—"}</div>
            <h3 class="task-title">${escapeHtml(task.title || "Без названия")}</h3>
          </div>
          <div class="task-meta">
            <span class="badge badge-status status-${status}">${formatStatus(status)}</span>
            <span class="badge badge-priority priority-${priority}">${formatPriority(priority)}</span>
          </div>
        </div>

        <p class="task-description">${escapeHtml(task.description || "Без описания")}</p>

        <div class="task-card__footer">
          <div class="task-created">
            <span class="task-created__label">Создано</span>
            <span class="task-created__value">${formatDate(task.created_at)}</span>
          </div>

          <div class="task-actions">
            ${renderStatusButtons(task.id, status)}
            <button type="button" class="action-btn action-btn-danger" data-action="delete" data-id="${task.id}">
              Удалить
            </button>
          </div>
        </div>
      </article>
    `;
  }).join("");
}

function renderStatusButtons(taskId, currentStatus) {
  const variants = [
    { value: "new", label: "Новая" },
    { value: "in_progress", label: "В работе" },
    { value: "done", label: "Готово" },
  ];

  return variants.map((item) => `
    <button
      type="button"
      class="action-btn ${item.value === currentStatus ? "is-current" : ""}"
      data-action="status"
      data-id="${taskId}"
      data-status="${item.value}"
      ${item.value === currentStatus ? 'aria-current="true"' : ""}
    >
      ${item.label}
    </button>
  `).join("");
}

async function createTask(event) {
  event.preventDefault();
  clearMessage();

  const title = document.getElementById("taskTitle")?.value.trim() || "";
  const description = document.getElementById("taskDescription")?.value.trim() || "";
  const priority = normalizePriority(document.getElementById("taskPriority")?.value || "medium");

  if (!title) {
    showMessage("Название задачи не может быть пустым.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/tasks`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify({ title, description, priority }),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      showMessage(data.error || data.message || "Не удалось создать задачу.", "error");
      return;
    }

    elements.taskForm?.reset();
    const priorityField = document.getElementById("taskPriority");
    if (priorityField) {
      priorityField.value = "medium";
    }
    showMessage("Задача добавлена.", "success");
    loadTasks({ preserveMessage: true });
  } catch (_error) {
    showMessage("Tasks API пока не реализован.", "warning");
  }
}

function handleTaskAction(event) {
  const button = event.target.closest("[data-action]");
  if (!button) return;

  const action = button.dataset.action;
  const taskId = Number(button.dataset.id);

  if (!taskId) return;

  if (action === "status") {
    const nextStatus = button.dataset.status || "new";
    updateTaskStatus(taskId, nextStatus);
  }

  if (action === "delete") {
    deleteTask(taskId);
  }
}

async function updateTaskStatus(taskId, status) {
  clearMessage();

  try {
    const response = await fetch(`${API_BASE}/tasks/${taskId}/status`, {
      method: "PATCH",
      headers: getAuthHeaders(true),
      body: JSON.stringify({ status }),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      showMessage(data.error || data.message || "Не удалось изменить статус.", "error");
      return;
    }

    showMessage("Статус обновлён.", "success");
    loadTasks({ preserveMessage: true });
  } catch (_error) {
    showMessage("Tasks API пока не реализован.", "warning");
  }
}

async function deleteTask(taskId) {
  clearMessage();

  try {
    const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: "DELETE",
      headers: getAuthHeaders(false),
    });

    if (!response.ok) {
      const data = await safeReadJson(response);
      showMessage(data.error || data.message || "Не удалось удалить задачу.", "error");
      return;
    }

    showMessage("Задача удалена.", "success");
    loadTasks({ preserveMessage: true });
  } catch (_error) {
    showMessage("Tasks API пока не реализован.", "warning");
  }
}

function logout() {
  state.token = "";
  state.username = "";
  state.tasks = [];

  localStorage.removeItem("token");
  localStorage.removeItem("username");

  showMessage("Сеанс завершён.", "success");
  updateView();
}

function normalizeStatus(value) {
  const status = String(value || "").toLowerCase().trim();
  if (status === "in progress") return "in_progress";
  if (status === "new" || status === "in_progress" || status === "done") return status;
  return "new";
}

function normalizePriority(value) {
  const priority = String(value || "").toLowerCase().trim();
  if (priority === "low" || priority === "medium" || priority === "high") return priority;
  return "medium";
}

function formatStatus(status) {
  if (status === "new") return "Новая";
  if (status === "in_progress") return "В работе";
  if (status === "done") return "Готово";
  return status;
}

function formatPriority(priority) {
  if (priority === "low") return "Низкий";
  if (priority === "medium") return "Средний";
  if (priority === "high") return "Высокий";
  return priority;
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";

  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

updateView();
