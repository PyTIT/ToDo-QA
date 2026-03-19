const API = "";

const state = {
  token: localStorage.getItem("token") || "",
  username: localStorage.getItem("username") || "",
  tasks: [],
  filter: "all",
};

const authSection = document.getElementById("authSection");
const appSection = document.getElementById("appSection");
const messageBox = document.getElementById("messageBox");
const authStateText = document.getElementById("authStateText");
const userText = document.getElementById("userText");
const tasksList = document.getElementById("tasksList");
const logoutBtn = document.getElementById("logoutBtn");

document.getElementById("registerForm").addEventListener("submit", registerUser);
document.getElementById("loginForm").addEventListener("submit", loginUser);
document.getElementById("taskForm").addEventListener("submit", createTask);
document.getElementById("reloadTasksBtn").addEventListener("click", loadTasks);
document.getElementById("logoutBtn").addEventListener("click", logout);

document.querySelectorAll(".filter-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.filter = btn.dataset.filter;
    renderTasks();
  });
});

document.getElementById("showLoginBtn").addEventListener("click", () => {
  authSection.classList.remove("hidden");
  appSection.classList.add("hidden");
});

document.getElementById("showRegisterBtn").addEventListener("click", () => {
  authSection.classList.remove("hidden");
  appSection.classList.add("hidden");
});

function showMessage(text, isError = false) {
  messageBox.textContent = text;
  messageBox.classList.remove("hidden");
  messageBox.style.background = isError ? "#fee2e2" : "#e0f2fe";
  messageBox.style.color = isError ? "#991b1b" : "#0c4a6e";
  messageBox.style.borderColor = isError ? "#fecaca" : "#bae6fd";
}

function clearMessage() {
  messageBox.classList.add("hidden");
  messageBox.textContent = "";
}

function updateLayout() {
  const isAuth = Boolean(state.token);

  authStateText.textContent = isAuth ? "Вы авторизованы" : "Вы не авторизованы";
  userText.textContent = `Пользователь: ${state.username || "—"}`;

  if (isAuth) {
    authSection.classList.add("hidden");
    appSection.classList.remove("hidden");
    logoutBtn.classList.remove("hidden");
    loadTasks();
  } else {
    authSection.classList.remove("hidden");
    appSection.classList.add("hidden");
    logoutBtn.classList.add("hidden");
    tasksList.innerHTML = "";
  }
}

async function registerUser(event) {
  event.preventDefault();
  clearMessage();

  const username = document.getElementById("registerUsername").value.trim();
  const password = document.getElementById("registerPassword").value.trim();

  try {
    const response = await fetch(`${API}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || "Ошибка регистрации", true);
      return;
    }

    showMessage("Регистрация успешна. Теперь войди в аккаунт.");
    event.target.reset();
  } catch (error) {
    showMessage("Сервер недоступен или произошла ошибка регистрации.", true);
  }
}

async function loginUser(event) {
  event.preventDefault();
  clearMessage();

  const username = document.getElementById("loginUsername").value.trim();
  const password = document.getElementById("loginPassword").value.trim();

  try {
    const response = await fetch(`${API}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || "Ошибка входа", true);
      return;
    }

    state.token = data.access_token;
    state.username = username;

    localStorage.setItem("token", state.token);
    localStorage.setItem("username", state.username);

    showMessage("Успешный вход.");
    event.target.reset();
    updateLayout();
  } catch (error) {
    showMessage("Сервер недоступен или произошла ошибка входа.", true);
  }
}

async function loadTasks() {
  clearMessage();

  try {
    const response = await fetch(`${API}/tasks`, {
      headers: {
        "Authorization": `Bearer ${state.token}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || "Не удалось загрузить задачи", true);
      return;
    }

    state.tasks = Array.isArray(data) ? data : [];
    renderTasks();
  } catch (error) {
    state.tasks = [];
    renderTasks();
    showMessage("Tasks API пока недоступен. Интерфейс готов, backend задач ещё нужно доделать.", true);
  }
}

function getFilteredTasks() {
  if (state.filter === "all") return state.tasks;
  return state.tasks.filter((task) => task.status === state.filter);
}

function renderTasks() {
  const tasks = getFilteredTasks();

  if (!tasks.length) {
    tasksList.innerHTML = `<div class="empty-state">Пока нет задач в этом фильтре.</div>`;
    return;
  }

  tasksList.innerHTML = tasks.map((task) => `
    <div class="task-card">
      <div class="task-top">
        <div>
          <h4 class="task-title">${escapeHtml(task.title || "Без названия")}</h4>
          <div class="badges">
            <span class="badge status-${task.status}">${formatStatus(task.status)}</span>
            <span class="badge priority-${task.priority}">Priority: ${task.priority}</span>
          </div>
        </div>
      </div>

      <p class="task-desc">${escapeHtml(task.description || "Без описания")}</p>

      <div class="task-actions">
        <button class="status-btn" onclick="changeTaskStatus(${task.id}, 'new')">New</button>
        <button class="status-btn" onclick="changeTaskStatus(${task.id}, 'in_progress')">In Progress</button>
        <button class="status-btn" onclick="changeTaskStatus(${task.id}, 'done')">Done</button>
        <button class="delete-btn" onclick="deleteTask(${task.id})">Удалить</button>
      </div>
    </div>
  `).join("");
}

async function createTask(event) {
  event.preventDefault();
  clearMessage();

  const title = document.getElementById("taskTitle").value.trim();
  const description = document.getElementById("taskDescription").value.trim();
  const priority = document.getElementById("taskPriority").value;

  try {
    const response = await fetch(`${API}/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${state.token}`,
      },
      body: JSON.stringify({ title, description, priority }),
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || "Не удалось создать задачу", true);
      return;
    }

    showMessage("Задача создана.");
    event.target.reset();
    loadTasks();
  } catch (error) {
    showMessage("Tasks API пока не реализован на backend.", true);
  }
}

async function changeTaskStatus(taskId, status) {
  clearMessage();

  try {
    const response = await fetch(`${API}/tasks/${taskId}/status`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${state.token}`,
      },
      body: JSON.stringify({ status }),
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || "Не удалось изменить статус", true);
      return;
    }

    showMessage("Статус обновлён.");
    loadTasks();
  } catch (error) {
    showMessage("Tasks API пока не реализован на backend.", true);
  }
}

async function deleteTask(taskId) {
  clearMessage();

  try {
    const response = await fetch(`${API}/tasks/${taskId}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${state.token}`,
      },
    });

    if (!response.ok) {
      let data = {};
      try {
        data = await response.json();
      } catch (_) {}
      showMessage(data.error || "Не удалось удалить задачу", true);
      return;
    }

    showMessage("Задача удалена.");
    loadTasks();
  } catch (error) {
    showMessage("Tasks API пока не реализован на backend.", true);
  }
}

function logout() {
  state.token = "";
  state.username = "";
  state.tasks = [];

  localStorage.removeItem("token");
  localStorage.removeItem("username");

  showMessage("Вы вышли из аккаунта.");
  updateLayout();
}

function formatStatus(status) {
  if (status === "new") return "New";
  if (status === "in_progress") return "In Progress";
  if (status === "done") return "Done";
  return status;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

updateLayout();