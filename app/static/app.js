const API_BASE = "";

const DEADLINE_OFFSET_MINUTES = 30;
const DEADLINE_STEP_MINUTES = 5;

const state = {
  token: localStorage.getItem("token") || "",
  username: localStorage.getItem("username") || "",
  tasks: [],
  allTasks: [],
  statusFilter: "all",
  search: "",
  sortBy: localStorage.getItem("sortBy") || "deadline_asc",
  theme: localStorage.getItem("theme") || "light",
  pendingDeleteTaskId: null,
  authMode: "login",
  isLoading: false,
  editingTaskOriginal: null,
  messageTimerId: null,
  loginCredentialsErrorActive: false
};

const customSelectRegistry = new WeakMap();
const buttonLabelRegistry = new WeakMap();
const taskActionState = new Map();

const CYRILLIC_RE = /[А-Яа-яЁё]/;
const LATIN_RE = /[A-Za-z]/;
const DIGIT_RE = /\d/;

const elements = {
  authSection: document.getElementById("authSection"),
  appSection: document.getElementById("appSection"),
  messageBox: document.getElementById("messageBox"),
  themeToggleBtn: document.getElementById("themeToggleBtn"),
  userText: document.getElementById("userText"),
  authStatusText: document.getElementById("authStatusText"),
  activeFilterText: document.getElementById("activeFilterText"),
  totalCount: document.getElementById("totalCount"),
  newCount: document.getElementById("newCount"),
  progressCount: document.getElementById("progressCount"),
  doneCount: document.getElementById("doneCount"),
  tasksSummary: document.getElementById("tasksSummary"),
  activeFilterChips: document.getElementById("activeFilterChips"),
  tasksList: document.getElementById("tasksList"),
  logoutBtn: document.getElementById("logoutBtn"),
  reloadTasksBtn: document.getElementById("reloadTasksBtn"),
  loginForm: document.getElementById("loginForm"),
  loginUsername: document.getElementById("loginUsername"),
  loginPassword: document.getElementById("loginPassword"),
  loginSubmitBtn: document.getElementById("loginSubmitBtn"),
  registerSubmitBtn: document.getElementById("registerSubmitBtn"),
  taskSubmitBtn: document.getElementById("taskSubmitBtn"),
  editTaskSubmitBtn: document.getElementById("editTaskSubmitBtn"),
  registerForm: document.getElementById("registerForm"),
  registerUsername: document.getElementById("registerUsername"),
  registerPassword: document.getElementById("registerPassword"),
  taskForm: document.getElementById("taskForm"),
  taskTitle: document.getElementById("taskTitle"),
  taskDescription: document.getElementById("taskDescription"),
  authModeTriggers: document.querySelectorAll("[data-auth-mode]"),
  authForms: document.querySelectorAll("[data-form-mode]"),
  searchInput: document.getElementById("searchInput"),
  statusFilterSelect: document.getElementById("statusFilterSelect"),
  sortSelect: document.getElementById("sortSelect"),
  applyFiltersBtn: document.getElementById("applyFiltersBtn"),
  resetFiltersBtn: document.getElementById("resetFiltersBtn"),
  taskDeadlineDate: document.getElementById("taskDeadlineDate"),
  taskDeadlineNative: document.getElementById("taskDeadlineNative"),
  taskDeadlineDateTrigger: document.getElementById("taskDeadlineDateTrigger"),
  taskDeadlineHour: document.getElementById("taskDeadlineHour"),
  taskDeadlineMinute: document.getElementById("taskDeadlineMinute"),
  taskDeadlineHourPrev: document.getElementById("taskDeadlineHourPrev"),
  taskDeadlineHourNext: document.getElementById("taskDeadlineHourNext"),
  taskDeadlineMinutePrev: document.getElementById("taskDeadlineMinutePrev"),
  taskDeadlineMinuteNext: document.getElementById("taskDeadlineMinuteNext"),
  clearTaskDeadlineBtn: document.getElementById("clearTaskDeadlineBtn"),
  taskTitleError: document.getElementById("taskTitleError"),
  taskDescriptionError: document.getElementById("taskDescriptionError"),
  taskDeadlineError: document.getElementById("taskDeadlineError"),
  taskTitleCounter: document.getElementById("taskTitleCounter"),
  taskDescriptionCounter: document.getElementById("taskDescriptionCounter"),
  loginUsernameError: document.getElementById("loginUsernameError"),
  loginPasswordError: document.getElementById("loginPasswordError"),
  registerUsernameError: document.getElementById("registerUsernameError"),
  registerPasswordError: document.getElementById("registerPasswordError"),
  editModal: document.getElementById("editModal"),
  closeEditModalBtn: document.getElementById("closeEditModalBtn"),
  cancelEditBtn: document.getElementById("cancelEditBtn"),
  editTaskForm: document.getElementById("editTaskForm"),
  editTaskId: document.getElementById("editTaskId"),
  editTaskTitle: document.getElementById("editTaskTitle"),
  editTaskDescription: document.getElementById("editTaskDescription"),
  editTaskPriority: document.getElementById("editTaskPriority"),
  editTaskDeadlineDate: document.getElementById("editTaskDeadlineDate"),
  editTaskDeadlineNative: document.getElementById("editTaskDeadlineNative"),
  editTaskDeadlineDateTrigger: document.getElementById("editTaskDeadlineDateTrigger"),
  editTaskDeadlineHour: document.getElementById("editTaskDeadlineHour"),
  editTaskDeadlineMinute: document.getElementById("editTaskDeadlineMinute"),
  editTaskDeadlineHourPrev: document.getElementById("editTaskDeadlineHourPrev"),
  editTaskDeadlineHourNext: document.getElementById("editTaskDeadlineHourNext"),
  editTaskDeadlineMinutePrev: document.getElementById("editTaskDeadlineMinutePrev"),
  editTaskDeadlineMinuteNext: document.getElementById("editTaskDeadlineMinuteNext"),
  clearEditDeadlineBtn: document.getElementById("clearEditDeadlineBtn"),
  editTaskTitleError: document.getElementById("editTaskTitleError"),
  editTaskDescriptionError: document.getElementById("editTaskDescriptionError"),
  editTaskDeadlineError: document.getElementById("editTaskDeadlineError"),
  editTaskTitleCounter: document.getElementById("editTaskTitleCounter"),
  editTaskDescriptionCounter: document.getElementById("editTaskDescriptionCounter"),
  deleteModal: document.getElementById("deleteModal"),
  closeDeleteModalBtn: document.getElementById("closeDeleteModalBtn"),
  cancelDeleteBtn: document.getElementById("cancelDeleteBtn"),
  confirmDeleteBtn: document.getElementById("confirmDeleteBtn"),
  deleteModalTaskText: document.getElementById("deleteModalTaskText"),
};

elements.loginForm?.addEventListener("submit", loginUser);
elements.registerForm?.addEventListener("submit", registerUser);
elements.taskForm?.addEventListener("submit", createTask);
elements.editTaskForm?.addEventListener("submit", submitTaskEdit);
elements.reloadTasksBtn?.addEventListener("click", () => loadTasks());
elements.logoutBtn?.addEventListener("click", logout);
elements.tasksList?.addEventListener("click", handleTaskAction);
elements.applyFiltersBtn?.addEventListener("click", applyFilters);
elements.resetFiltersBtn?.addEventListener("click", resetFilters);
elements.closeEditModalBtn?.addEventListener("click", closeEditModal);
elements.cancelEditBtn?.addEventListener("click", closeEditModal);
elements.editModal?.addEventListener("click", handleModalClick);
elements.themeToggleBtn?.addEventListener("click", toggleTheme);
elements.closeDeleteModalBtn?.addEventListener("click", closeDeleteModal);
elements.cancelDeleteBtn?.addEventListener("click", closeDeleteModal);
elements.confirmDeleteBtn?.addEventListener("click", confirmDeleteTask);
elements.deleteModal?.addEventListener("click", handleDeleteModalClick);
elements.activeFilterChips?.addEventListener("click", handleFilterChipAction);

bindDeadlinePicker({
  dateInput: elements.taskDeadlineDate,
  nativeDateInput: elements.taskDeadlineNative,
  dateTriggerButton: elements.taskDeadlineDateTrigger,
  hourInput: elements.taskDeadlineHour,
  minuteInput: elements.taskDeadlineMinute,
  hourPrevButton: elements.taskDeadlineHourPrev,
  hourNextButton: elements.taskDeadlineHourNext,
  minutePrevButton: elements.taskDeadlineMinutePrev,
  minuteNextButton: elements.taskDeadlineMinuteNext,
  clearButton: elements.clearTaskDeadlineBtn,
  preserveCurrentValue: false,
  onChange: () => validateDeadlineField("create"),
});
bindDeadlinePicker({
  dateInput: elements.editTaskDeadlineDate,
  nativeDateInput: elements.editTaskDeadlineNative,
  dateTriggerButton: elements.editTaskDeadlineDateTrigger,
  hourInput: elements.editTaskDeadlineHour,
  minuteInput: elements.editTaskDeadlineMinute,
  hourPrevButton: elements.editTaskDeadlineHourPrev,
  hourNextButton: elements.editTaskDeadlineHourNext,
  minutePrevButton: elements.editTaskDeadlineMinutePrev,
  minuteNextButton: elements.editTaskDeadlineMinuteNext,
  clearButton: elements.clearEditDeadlineBtn,
  preserveCurrentValue: true,
  onChange: () => validateDeadlineField("edit"),
});

window.addEventListener("focus", refreshDeadlinePickers);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    refreshDeadlinePickers();
  }
});

elements.searchInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    applyFilters();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeEditModal();
    closeDeleteModal();
    closeAllCustomSelects();
  }
});

elements.authModeTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => {
    const nextMode = trigger.dataset.authMode;
    if (!nextMode) return;
    setAuthMode(nextMode);
  });
});

setupCustomSelects();
setupInlineFieldUX();

document.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  if (target.closest(".select-shell")) {
    return;
  }

  closeAllCustomSelects();
});

document.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  if (target.closest(".select-shell")) {
    return;
  }

  if (
    state.loginCredentialsErrorActive &&
    elements.loginForm &&
    !elements.loginForm.contains(target)
  ) {
    clearLoginCredentialsError();
  }

  closeAllCustomSelects();
});

function rememberButtonLabel(button) {
  if (!(button instanceof HTMLButtonElement)) {
    return "";
  }

  if (!buttonLabelRegistry.has(button)) {
    buttonLabelRegistry.set(button, button.textContent || "");
  }

  return buttonLabelRegistry.get(button) || "";
}

function setButtonBusy(button, isBusy, busyLabel = "Сохраняем...") {
  if (!(button instanceof HTMLButtonElement)) return;

  const defaultLabel = rememberButtonLabel(button);

  if (isBusy) {
    button.disabled = true;
    button.classList.add("is-loading");
    button.textContent = busyLabel;
    return;
  }

  button.disabled = false;
  button.classList.remove("is-loading");
  button.textContent = defaultLabel;
}

function setCounter(counter, value, limit) {
  if (!(counter instanceof HTMLElement)) return;

  const currentLength = String(value || "").length;
  counter.textContent = `${currentLength}/${limit}`;
  counter.classList.toggle("is-warning", limit - currentLength <= 15 && currentLength <= limit);
  counter.classList.toggle("is-error", currentLength > limit);
}

function setControlInvalid(control, isInvalid = true) {
  if (!(control instanceof HTMLElement)) return;

  control.classList.toggle("is-invalid", isInvalid);
  control.setAttribute("aria-invalid", isInvalid ? "true" : "false");
}

function setInlineMessage(control, feedbackNode, message = "") {
  if (control instanceof HTMLElement) {
    control.classList.toggle("is-invalid", Boolean(message));
    control.setAttribute("aria-invalid", message ? "true" : "false");
  }

  if (!(feedbackNode instanceof HTMLElement)) return;

  feedbackNode.textContent = message;
  feedbackNode.classList.toggle("hidden", !message);
}

function setLoginCredentialsError(message = "Неверный логин или пароль.") {
  state.loginCredentialsErrorActive = true;

  setControlInvalid(elements.loginUsername, true);
  setControlInvalid(elements.loginPassword, true);

  if (elements.loginUsernameError) {
    elements.loginUsernameError.textContent = "";
    elements.loginUsernameError.classList.add("hidden");
  }

  setInlineMessage(elements.loginPassword, elements.loginPasswordError, message);
}

function clearLoginCredentialsError() {
  if (!state.loginCredentialsErrorActive) return;

  state.loginCredentialsErrorActive = false;

  clearInlineMessage(elements.loginUsername, elements.loginUsernameError);
  clearInlineMessage(elements.loginPassword, elements.loginPasswordError);

  if (elements.loginUsername) elements.loginUsername.dataset.touched = "false";
  if (elements.loginPassword) elements.loginPassword.dataset.touched = "false";
}

function clearInlineMessage(control, feedbackNode) {
  setInlineMessage(control, feedbackNode, "");
}

function focusFirstInvalidControl(configs) {
  const invalidConfig = configs.find((config) => config?.validator?.());
  invalidConfig?.input?.focus();
}

function hasWhitespace(value) {
  return /\s/.test(String(value || ""));
}

function getUsernameError(value) {
  const safeValue = String(value || "");

  if (!safeValue.trim()) return "Логин обязателен.";
  if (hasWhitespace(safeValue)) return "Логин не должен содержать пробелы.";
  if (safeValue.length < 3 || safeValue.length > 30) return "Логин должен быть от 3 до 30 символов.";
  if (CYRILLIC_RE.test(safeValue)) return "Логин не должен содержать кириллицу.";
  if (/^\d+$/.test(safeValue)) return "Логин не должен состоять только из цифр.";

  return "";
}

function getPasswordError(value) {
  const safeValue = String(value || "");

  if (!safeValue) return "Пароль обязателен.";
  if (hasWhitespace(safeValue)) return "Пароль не должен содержать пробелы.";
  if (safeValue.length < 8 || safeValue.length > 32) return "Пароль должен быть от 8 до 32 символов.";
  if (CYRILLIC_RE.test(safeValue)) return "Пароль не должен содержать кириллицу.";
  if (!LATIN_RE.test(safeValue)) return "Пароль должен содержать хотя бы одну латинскую букву.";
  if (!DIGIT_RE.test(safeValue)) return "Пароль должен содержать хотя бы одну цифру.";

  return "";
}

function getTitleError(value) {
  const trimmedValue = String(value || "").trim();

  if (!trimmedValue) return "Название задачи обязательно.";
  if (trimmedValue.length > 80) return "Название должно быть не длиннее 80 символов.";

  return "";
}

function getDescriptionError(value) {
  const safeValue = String(value || "");

  if (safeValue.length > 500) return "Описание должно быть не длиннее 500 символов.";

  return "";
}

function getDeadlineValue(mode) {
  if (mode === "edit") {
    return combineDeadlineParts(
      getCanonicalDateValue(elements.editTaskDeadlineDate),
      elements.editTaskDeadlineHour?.value || "",
      elements.editTaskDeadlineMinute?.value || "",
    );
  }

  return combineDeadlineParts(
    getCanonicalDateValue(elements.taskDeadlineDate),
    elements.taskDeadlineHour?.value || "",
    elements.taskDeadlineMinute?.value || "",
  );
}

function validateDeadlineField(mode = "create", { force = false } = {}) {
  const isEdit = mode === "edit";
  const dateInput = isEdit ? elements.editTaskDeadlineDate : elements.taskDeadlineDate;
  const feedbackNode = isEdit ? elements.editTaskDeadlineError : elements.taskDeadlineError;

  if (!(dateInput instanceof HTMLInputElement)) {
    return "";
  }

  const isTouched = dateInput.dataset.touched === "true";
  const deadlineValue = getDeadlineValue(mode);
  const shouldValidate = force || isTouched || Boolean(getCanonicalDateValue(dateInput));
  const message = shouldValidate && deadlineValue && !isAtLeastThirtyMinutesAhead(deadlineValue)
    ? "Дедлайн должен быть минимум на 30 минут позже текущего времени."
    : "";

  setInlineMessage(dateInput, feedbackNode, message);
  return message;
}

function clearTaskFormInlineState(mode = "create") {
  if (mode === "edit") {
    if (elements.editTaskTitle) elements.editTaskTitle.dataset.touched = "false";
    if (elements.editTaskDescription) elements.editTaskDescription.dataset.touched = "false";
    if (elements.editTaskDeadlineDate) elements.editTaskDeadlineDate.dataset.touched = "false";
    clearInlineMessage(elements.editTaskTitle, elements.editTaskTitleError);
    clearInlineMessage(elements.editTaskDescription, elements.editTaskDescriptionError);
    clearInlineMessage(elements.editTaskDeadlineDate, elements.editTaskDeadlineError);
    setCounter(elements.editTaskTitleCounter, elements.editTaskTitle?.value || "", 80);
    setCounter(elements.editTaskDescriptionCounter, elements.editTaskDescription?.value || "", 500);
    return;
  }

  if (elements.taskTitle) elements.taskTitle.dataset.touched = "false";
  if (elements.taskDescription) elements.taskDescription.dataset.touched = "false";
  if (elements.taskDeadlineDate) elements.taskDeadlineDate.dataset.touched = "false";
  clearInlineMessage(elements.taskTitle, elements.taskTitleError);
  clearInlineMessage(elements.taskDescription, elements.taskDescriptionError);
  clearInlineMessage(elements.taskDeadlineDate, elements.taskDeadlineError);
  setCounter(elements.taskTitleCounter, elements.taskTitle?.value || "", 80);
  setCounter(elements.taskDescriptionCounter, elements.taskDescription?.value || "", 500);
}

function setupValidatedInput(input, feedbackNode, validator, { counter = null, limit = null } = {}) {
  if (!(input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement)) {
    return;
  }

  const applyValidation = ({ force = false } = {}) => {
    const isTouched = input.dataset.touched === "true";
    const shouldValidate = force || isTouched || Boolean(String(input.value || ""));
    const message = shouldValidate ? validator() : "";
    setInlineMessage(input, feedbackNode, message);
    return message;
  };

  if (limit && counter) {
    setCounter(counter, input.value, limit);
  }

  input.dataset.touched = input.dataset.touched || "false";

  input.addEventListener("input", () => {
    if (limit && counter) {
      setCounter(counter, input.value, limit);
    }

    applyValidation();
  });

  input.addEventListener("blur", () => {
    input.dataset.touched = "true";
    applyValidation({ force: true });
  });
}

function setupInlineFieldUX() {
  setupValidatedInput(elements.loginUsername, elements.loginUsernameError, () => getUsernameError(elements.loginUsername?.value || ""));
  setupValidatedInput(elements.loginPassword, elements.loginPasswordError, () => getPasswordError(elements.loginPassword?.value || ""));
  setupValidatedInput(elements.registerUsername, elements.registerUsernameError, () => getUsernameError(elements.registerUsername?.value || ""));
  setupValidatedInput(elements.registerPassword, elements.registerPasswordError, () => getPasswordError(elements.registerPassword?.value || ""));
  setupValidatedInput(elements.taskTitle, elements.taskTitleError, () => getTitleError(elements.taskTitle?.value || ""), { counter: elements.taskTitleCounter, limit: 80 });
  setupValidatedInput(elements.taskDescription, elements.taskDescriptionError, () => getDescriptionError(elements.taskDescription?.value || ""), { counter: elements.taskDescriptionCounter, limit: 500 });
  setupValidatedInput(elements.editTaskTitle, elements.editTaskTitleError, () => getTitleError(elements.editTaskTitle?.value || ""), { counter: elements.editTaskTitleCounter, limit: 80 });
  setupValidatedInput(elements.editTaskDescription, elements.editTaskDescriptionError, () => getDescriptionError(elements.editTaskDescription?.value || ""), { counter: elements.editTaskDescriptionCounter, limit: 500 });

  clearTaskFormInlineState("create");
  clearTaskFormInlineState("edit");
}

function validateAuthFields(mode) {
  const configs = mode === "register"
    ? [
        { input: elements.registerUsername, validator: () => setInlineMessage(elements.registerUsername, elements.registerUsernameError, getUsernameError(elements.registerUsername?.value || "")) || getUsernameError(elements.registerUsername?.value || "") },
        { input: elements.registerPassword, validator: () => setInlineMessage(elements.registerPassword, elements.registerPasswordError, getPasswordError(elements.registerPassword?.value || "")) || getPasswordError(elements.registerPassword?.value || "") },
      ]
    : [
        { input: elements.loginUsername, validator: () => setInlineMessage(elements.loginUsername, elements.loginUsernameError, getUsernameError(elements.loginUsername?.value || "")) || getUsernameError(elements.loginUsername?.value || "") },
        { input: elements.loginPassword, validator: () => setInlineMessage(elements.loginPassword, elements.loginPasswordError, getPasswordError(elements.loginPassword?.value || "")) || getPasswordError(elements.loginPassword?.value || "") },
      ];

  let isValid = true;
  configs.forEach(({ input, validator }) => {
    if (input) input.dataset.touched = "true";
    const message = validator();
    if (message) isValid = false;
  });

  if (!isValid) {
    focusFirstInvalidControl(configs);
  }

  return isValid;
}

function validateTaskFields(mode = "create") {
  const isEdit = mode === "edit";
  const titleInput = isEdit ? elements.editTaskTitle : elements.taskTitle;
  const titleErrorNode = isEdit ? elements.editTaskTitleError : elements.taskTitleError;
  const descriptionInput = isEdit ? elements.editTaskDescription : elements.taskDescription;
  const descriptionErrorNode = isEdit ? elements.editTaskDescriptionError : elements.taskDescriptionError;

  if (titleInput) titleInput.dataset.touched = "true";
  if (descriptionInput) descriptionInput.dataset.touched = "true";
  if (isEdit ? elements.editTaskDeadlineDate : elements.taskDeadlineDate) {
    (isEdit ? elements.editTaskDeadlineDate : elements.taskDeadlineDate).dataset.touched = "true";
  }

  const titleMessage = getTitleError(titleInput?.value || "");
  const descriptionMessage = getDescriptionError(descriptionInput?.value || "");
  setInlineMessage(titleInput, titleErrorNode, titleMessage);
  setInlineMessage(descriptionInput, descriptionErrorNode, descriptionMessage);
  const deadlineMessage = validateDeadlineField(mode, { force: true });

  const isValid = !titleMessage && !descriptionMessage && !deadlineMessage;
  if (!isValid) {
    if (titleMessage) {
      titleInput?.focus();
    } else if (descriptionMessage) {
      descriptionInput?.focus();
    }
  }

  return isValid;
}

function clearAuthInlineErrors(mode) {
  if (mode === "register") {
    clearInlineMessage(elements.registerUsername, elements.registerUsernameError);
    clearInlineMessage(elements.registerPassword, elements.registerPasswordError);
    if (elements.registerUsername) elements.registerUsername.dataset.touched = "false";
    if (elements.registerPassword) elements.registerPassword.dataset.touched = "false";
    return;
  }

  clearInlineMessage(elements.loginUsername, elements.loginUsernameError);
  clearInlineMessage(elements.loginPassword, elements.loginPasswordError);
  if (elements.loginUsername) elements.loginUsername.dataset.touched = "false";
  if (elements.loginPassword) elements.loginPassword.dataset.touched = "false";
}

function mapServerMessageToField(message, mode = "create") {
  const safeMessage = String(message || "");

  if (!safeMessage) return false;

  if (mode === "login" || mode === "register") {
    if (safeMessage.includes("Username")) {
      const target = mode === "register" ? elements.registerUsername : elements.loginUsername;
      const feedback = mode === "register" ? elements.registerUsernameError : elements.loginUsernameError;
      setInlineMessage(target, feedback, safeMessage === "Username already exists" ? "Такой логин уже существует." : safeMessage);
      target?.focus();
      return true;
    }

    if (safeMessage.includes("Password")) {
      const target = mode === "register" ? elements.registerPassword : elements.loginPassword;
      const feedback = mode === "register" ? elements.registerPasswordError : elements.loginPasswordError;
      setInlineMessage(target, feedback, safeMessage);
      target?.focus();
      return true;
    }

    if (mode === "login" && safeMessage.includes("Invalid username or password")) {
      const authErrorText = "Неверный логин или пароль.";

      if (mode === "login" && safeMessage.includes("Invalid username or password")) {
        setLoginCredentialsError("Неверный логин или пароль.");
        elements.loginPassword?.focus();
        return true;
      }
    }

    return false;
  }

  if (safeMessage.includes("Title")) {
    const target = mode === "edit" ? elements.editTaskTitle : elements.taskTitle;
    const feedback = mode === "edit" ? elements.editTaskTitleError : elements.taskTitleError;
    setInlineMessage(target, feedback, safeMessage === "Title is required" ? "Название задачи обязательно." : safeMessage);
    target?.focus();
    return true;
  }

  if (safeMessage.includes("Description")) {
    const target = mode === "edit" ? elements.editTaskDescription : elements.taskDescription;
    const feedback = mode === "edit" ? elements.editTaskDescriptionError : elements.taskDescriptionError;
    setInlineMessage(target, feedback, safeMessage);
    target?.focus();
    return true;
  }

  if (safeMessage.includes("Deadline")) {
    const target = mode === "edit" ? elements.editTaskDeadlineDate : elements.taskDeadlineDate;
    const feedback = mode === "edit" ? elements.editTaskDeadlineError : elements.taskDeadlineError;
    setInlineMessage(target, feedback, safeMessage === "Deadline must be at least 30 minutes later than current time" ? "Дедлайн должен быть минимум на 30 минут позже текущего времени." : safeMessage);
    target?.focus();
    return true;
  }

  return false;
}

function getTaskAction(taskId) {
  return taskActionState.get(Number(taskId)) || null;
}

function setTaskAction(taskId, action = null) {
  const safeTaskId = Number(taskId);
  if (!safeTaskId) return;

  if (action) {
    taskActionState.set(safeTaskId, action);
  } else {
    taskActionState.delete(safeTaskId);
  }

  renderTasks();
}

function renderActiveFilterChips() {
  if (!elements.activeFilterChips) return;

  const chips = [];

  if (state.statusFilter !== "all") {
    chips.push({ label: `Статус: ${formatFilterLabel(state.statusFilter)}`, key: "status" });
  }

  if (state.search) {
    chips.push({ label: `Поиск: ${state.search}`, key: "search" });
  }

  if (state.sortBy !== "deadline_asc") {
    chips.push({ label: `Сортировка: ${formatSortLabel(state.sortBy)}`, key: "sort" });
  }

  if (!chips.length) {
    elements.activeFilterChips.innerHTML = "";
    elements.activeFilterChips.classList.add("hidden");
    return;
  }

  elements.activeFilterChips.innerHTML = chips.map((chip) => `
    <button type="button" class="filter-chip" data-clear-filter="${chip.key}">
      <span class="filter-chip__label">${escapeHtml(chip.label)}</span>
      <span class="filter-chip__remove" aria-hidden="true">×</span>
    </button>
  `).join("");
  elements.activeFilterChips.classList.remove("hidden");
}

function handleFilterChipAction(event) {
  const button = event.target instanceof HTMLElement ? event.target.closest("[data-clear-filter]") : null;
  if (!(button instanceof HTMLButtonElement)) return;

  const filterKey = button.dataset.clearFilter;
  if (filterKey === "status") {
    state.statusFilter = "all";
  }
  if (filterKey === "search") {
    state.search = "";
  }
  if (filterKey === "sort") {
    state.sortBy = "deadline_asc";
  }

  localStorage.setItem("sortBy", state.sortBy);
  syncFilterControls();
  updateFilterCaption();
  renderActiveFilterChips();
  loadTasks();
}

function applyTheme(theme) {
  const nextTheme = theme === "dark" ? "dark" : "light";
  state.theme = nextTheme;
  document.body?.setAttribute("data-theme", nextTheme);
  localStorage.setItem("theme", nextTheme);
  updateThemeToggle();
}

function updateThemeToggle() {
  if (!elements.themeToggleBtn) return;

  const isDark = state.theme === "dark";
  elements.themeToggleBtn.textContent = isDark ? "Светлая тема" : "Тёмная тема";
  elements.themeToggleBtn.setAttribute("aria-pressed", isDark ? "true" : "false");
  elements.themeToggleBtn.setAttribute("aria-label", isDark ? "Переключить на светлую тему" : "Переключить на тёмную тему");
}

function toggleTheme() {
  applyTheme(state.theme === "dark" ? "light" : "dark");
}

function showMessage(text, kind = "info") {
  if (!elements.messageBox) return;

  if (state.messageTimerId) {
    window.clearTimeout(state.messageTimerId);
    state.messageTimerId = null;
  }

  elements.messageBox.textContent = text;
  elements.messageBox.classList.remove("hidden", "is-error", "is-success", "is-warning");

  if (kind === "error") {
    elements.messageBox.classList.add("is-error");
  } else if (kind === "success") {
    elements.messageBox.classList.add("is-success");
  } else if (kind === "warning") {
    elements.messageBox.classList.add("is-warning");
  }

  state.messageTimerId = window.setTimeout(() => {
    clearMessage();
  }, 3000);
}

function clearMessage() {
  if (!elements.messageBox) return;

  if (state.messageTimerId) {
    window.clearTimeout(state.messageTimerId);
    state.messageTimerId = null;
  }

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
}

function updateStats() {
  const sourceTasks = Array.isArray(state.allTasks) ? state.allTasks : [];
  const total = sourceTasks.length;
  const totalNew = sourceTasks.filter((task) => normalizeStatus(task.status) === "new").length;
  const totalInProgress = sourceTasks.filter((task) => normalizeStatus(task.status) === "in_progress").length;
  const totalDone = sourceTasks.filter((task) => normalizeStatus(task.status) === "done").length;

  safeSetText(elements.totalCount, String(total));
  safeSetText(elements.newCount, String(totalNew));
  safeSetText(elements.progressCount, String(totalInProgress));
  safeSetText(elements.doneCount, String(totalDone));
}

function updateFilterCaption() {
  const statusLabel = formatFilterLabel(state.statusFilter);
  const searchLabel = state.search ? ` • поиск: ${state.search}` : "";
  const sortLabel = ` • сортировка: ${formatSortLabel(state.sortBy)}`;
  safeSetText(elements.activeFilterText, `${statusLabel}${searchLabel}${sortLabel}`);
  renderActiveFilterChips();
}

function updateSummary() {
  if (!elements.tasksSummary) return;

  const count = state.tasks.length;
  const statusLabel = formatFilterLabel(state.statusFilter);

  if (!count) {
    elements.tasksSummary.textContent = state.search
      ? `По запросу «${state.search}» ничего не найдено.`
      : `Сейчас нет задач в выборке «${statusLabel}».`;
    return;
  }

  const base = count === 1 ? "1 задача" : `${count} задач`;
  const searchPart = state.search ? ` по запросу «${state.search}»` : "";
  elements.tasksSummary.textContent = `${base} в выборке «${statusLabel}»${searchPart}.`;
}

function updateView() {
  const isAuthorized = Boolean(state.token);

  safeSetText(elements.userText, state.username || "—");
  safeSetText(elements.authStatusText, isAuthorized ? "Авторизован" : "Не авторизован");

  elements.logoutBtn?.classList.toggle("hidden", !isAuthorized);
  elements.authSection?.classList.toggle("hidden", isAuthorized);
  elements.appSection?.classList.toggle("hidden", !isAuthorized);

  if (isAuthorized) {
    syncFilterControls();
    updateFilterCaption();
    loadTasks();
  } else {
    applyTasksStateChanges([]);
    renderActiveFilterChips();
  }

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

function syncFilterControls() {
  if (elements.searchInput) {
    elements.searchInput.value = state.search;
  }
  if (elements.statusFilterSelect) {
    elements.statusFilterSelect.value = state.statusFilter;
    refreshCustomSelect(elements.statusFilterSelect);
  }
  if (elements.sortSelect) {
    elements.sortSelect.value = state.sortBy;
    refreshCustomSelect(elements.sortSelect);
  }
}


function setupCustomSelects() {
  const selects = document.querySelectorAll(".select-shell select");

  selects.forEach((select, index) => {
    if (!(select instanceof HTMLSelectElement)) {
      return;
    }

    const shell = select.closest(".select-shell");
    if (!(shell instanceof HTMLElement) || customSelectRegistry.has(select)) {
      return;
    }

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "select-shell__trigger";
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");

    const triggerLabel = document.createElement("span");
    triggerLabel.className = "select-shell__trigger-label";
    trigger.appendChild(triggerLabel);

    const dropdown = document.createElement("div");
    dropdown.className = "select-shell__dropdown hidden";
    dropdown.setAttribute("role", "listbox");

    const optionButtons = [];
    const dropdownId = select.id ? `${select.id}CustomListbox` : `customSelectListbox${index + 1}`;
    dropdown.id = dropdownId;
    trigger.setAttribute("aria-controls", dropdownId);

    Array.from(select.options).forEach((option) => {
      const optionButton = document.createElement("button");
      optionButton.type = "button";
      optionButton.className = "select-shell__option";
      optionButton.dataset.value = option.value;
      optionButton.textContent = option.textContent || option.value;
      optionButton.setAttribute("role", "option");
      optionButton.tabIndex = -1;

      optionButton.addEventListener("click", () => {
        if (select.value === option.value) {
          closeCustomSelect(select);
          return;
        }

        select.value = option.value;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        refreshCustomSelect(select);
        closeCustomSelect(select);
        trigger.focus();
      });

      dropdown.appendChild(optionButton);
      optionButtons.push(optionButton);
    });

    shell.append(trigger, dropdown);

    const sync = () => {
      const selectedOption = select.options[select.selectedIndex] || select.options[0] || null;
      const selectedLabel = selectedOption?.textContent?.trim() || "Выберите значение";
      triggerLabel.textContent = selectedLabel;
      trigger.title = selectedLabel;

      optionButtons.forEach((button) => {
        const isSelected = button.dataset.value === select.value;
        button.classList.toggle("is-selected", isSelected);
        button.setAttribute("aria-selected", isSelected ? "true" : "false");
      });
    };

    const open = ({ focusSelected = false } = {}) => {
      closeAllCustomSelects(select);
      shell.classList.add("is-open");
      dropdown.classList.remove("hidden");
      trigger.setAttribute("aria-expanded", "true");

      if (focusSelected) {
        const selectedButton = optionButtons.find((button) => button.dataset.value === select.value) || optionButtons[0];
        selectedButton?.focus();
      }
    };

    const close = () => {
      shell.classList.remove("is-open");
      dropdown.classList.add("hidden");
      trigger.setAttribute("aria-expanded", "false");
    };

    const focusOptionByStep = (step) => {
      const currentIndex = optionButtons.findIndex((button) => button.dataset.value === select.value);
      const fallbackIndex = step > 0 ? 0 : optionButtons.length - 1;
      const nextIndex = currentIndex >= 0
        ? (currentIndex + step + optionButtons.length) % optionButtons.length
        : fallbackIndex;
      const nextButton = optionButtons[nextIndex];
      if (!nextButton) return;

      select.value = nextButton.dataset.value || select.value;
      select.dispatchEvent(new Event("change", { bubbles: true }));
      refreshCustomSelect(select);
    };

    trigger.addEventListener("click", () => {
      if (shell.classList.contains("is-open")) {
        close();
        return;
      }

      open();
    });

    trigger.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        open({ focusSelected: true });
        return;
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        open({ focusSelected: true });
      }
    });

    dropdown.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close();
        trigger.focus();
        return;
      }

      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        const currentIndex = optionButtons.findIndex((button) => button === document.activeElement);
        const currentButton = currentIndex >= 0 ? optionButtons[currentIndex] : optionButtons.find((button) => button.dataset.value === select.value) || optionButtons[0];
        const baseIndex = optionButtons.indexOf(currentButton);
        const step = event.key === "ArrowDown" ? 1 : -1;
        const nextIndex = (baseIndex + step + optionButtons.length) % optionButtons.length;
        optionButtons[nextIndex]?.focus();
        return;
      }

      if (event.key === "Enter" || event.key === " ") {
        const focusedButton = document.activeElement;
        if (!(focusedButton instanceof HTMLButtonElement) || !focusedButton.classList.contains("select-shell__option")) {
          return;
        }

        event.preventDefault();
        focusedButton.click();
      }
    });

    select.addEventListener("change", sync);

    customSelectRegistry.set(select, {
      shell,
      trigger,
      dropdown,
      optionButtons,
      sync,
      close,
      open,
      focusOptionByStep,
    });

    sync();
  });
}

function refreshCustomSelect(select) {
  if (!(select instanceof HTMLSelectElement)) {
    return;
  }

  customSelectRegistry.get(select)?.sync();
}

function closeCustomSelect(select) {
  if (!(select instanceof HTMLSelectElement)) {
    return;
  }

  customSelectRegistry.get(select)?.close();
}

function closeAllCustomSelects(exceptSelect = null) {
  document.querySelectorAll(".select-shell select").forEach((select) => {
    if (!(select instanceof HTMLSelectElement) || select === exceptSelect) {
      return;
    }

    closeCustomSelect(select);
  });
}

function bindDeadlinePicker({
  dateInput,
  nativeDateInput,
  dateTriggerButton,
  hourInput,
  minuteInput,
  hourPrevButton,
  hourNextButton,
  minutePrevButton,
  minuteNextButton,
  clearButton,
  preserveCurrentValue = false,
  onChange,
}) {
  if (!(dateInput instanceof HTMLInputElement) || !(hourInput instanceof HTMLInputElement) || !(minuteInput instanceof HTMLInputElement)) {
    return;
  }

  const sync = () => {
    syncDeadlinePicker({
      dateInput,
      nativeDateInput,
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      preserveCurrentValue,
    });
    onChange?.();
  };

  dateInput.addEventListener("input", () => {
    applyDateInputMask(dateInput);
    const parsedDate = parseDisplayDateValue(dateInput.value);
    dateInput.dataset.canonicalDate = parsedDate;
    const canonicalDate = parsedDate;
    if (nativeDateInput instanceof HTMLInputElement) {
      nativeDateInput.min = formatInputDate(getMinimumDeadlineDate());
      nativeDateInput.value = canonicalDate;
    }
    sync();
  });

  dateInput.addEventListener("blur", () => {
    dateInput.dataset.touched = "true";
    normalizeDateTextValue(dateInput, nativeDateInput, preserveCurrentValue);
    sync();
  });

  const handleNativeDateSelection = () => {
    dateInput.dataset.touched = "true";
    setDatePickerValue(dateInput, nativeDateInput, nativeDateInput?.value || "");
    sync();
  };

  elements.loginUsername?.addEventListener("input", clearLoginCredentialsError);
  elements.loginPassword?.addEventListener("input", clearLoginCredentialsError);

  nativeDateInput?.addEventListener("input", handleNativeDateSelection);
  nativeDateInput?.addEventListener("change", handleNativeDateSelection);

  dateTriggerButton?.addEventListener("click", () => {
    if (!(nativeDateInput instanceof HTMLInputElement)) {
      return;
    }

    const minDateValue = formatInputDate(getMinimumDeadlineDate());
    const currentDateValue = getCanonicalDateValue(dateInput);

    nativeDateInput.min = minDateValue;
    nativeDateInput.value = currentDateValue || "";

    if (typeof nativeDateInput.showPicker === "function") {
      nativeDateInput.showPicker();
      return;
    }

    nativeDateInput.focus();
    nativeDateInput.click();
  });

  hourPrevButton?.addEventListener("click", () => {
    dateInput.dataset.touched = "true";
    shiftDeadlineTime({
      dateInput,
      nativeDateInput,
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      deltaMinutes: -60,
      preserveCurrentValue,
    });
  });

  hourNextButton?.addEventListener("click", () => {
    dateInput.dataset.touched = "true";
    shiftDeadlineTime({
      dateInput,
      nativeDateInput,
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      deltaMinutes: 60,
      preserveCurrentValue,
    });
  });

  minutePrevButton?.addEventListener("click", () => {
    dateInput.dataset.touched = "true";
    shiftDeadlineTime({
      dateInput,
      nativeDateInput,
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      deltaMinutes: -DEADLINE_STEP_MINUTES,
      preserveCurrentValue,
    });
  });

  minuteNextButton?.addEventListener("click", () => {
    dateInput.dataset.touched = "true";
    shiftDeadlineTime({
      dateInput,
      nativeDateInput,
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      deltaMinutes: DEADLINE_STEP_MINUTES,
      preserveCurrentValue,
    });
  });

  clearButton?.addEventListener("click", () => {
    dateInput.dataset.touched = "false";
    clearDeadlinePicker(dateInput, nativeDateInput, hourInput, minuteInput, hourPrevButton, hourNextButton, minutePrevButton, minuteNextButton);
    onChange?.();
  });

  sync();
}

function applyDateInputMask(dateInput) {
  if (!(dateInput instanceof HTMLInputElement)) {
    return;
  }

  const digits = String(dateInput.value || "").replace(/\D/g, "").slice(0, 8);
  let formatted = digits.slice(0, 2);

  if (digits.length > 2) {
    formatted += `.${digits.slice(2, 4)}`;
  }
  if (digits.length > 4) {
    formatted += `.${digits.slice(4, 8)}`;
  }

  dateInput.value = formatted;
}

function parseDisplayDateValue(value) {
  const normalized = String(value || "").trim();
  const match = normalized.match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
  if (!match) {
    return "";
  }

  const [, dayRaw, monthRaw, yearRaw] = match;
  const day = Number(dayRaw);
  const month = Number(monthRaw);
  const year = Number(yearRaw);

  if (!day || !month || !year) {
    return "";
  }

  const candidate = new Date(year, month - 1, day, 12, 0, 0, 0);
  if (
    candidate.getFullYear() !== year
    || candidate.getMonth() !== month - 1
    || candidate.getDate() !== day
  ) {
    return "";
  }

  return `${yearRaw}-${monthRaw}-${dayRaw}`;
}

function formatDisplayDate(dateValue) {
  const safeDate = String(dateValue || "").trim();
  const match = safeDate.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) {
    return "";
  }

  const [, year, month, day] = match;
  return `${day}.${month}.${year}`;
}

function getCanonicalDateValue(dateInput) {
  if (!(dateInput instanceof HTMLInputElement)) {
    return "";
  }

  const parsed = parseDisplayDateValue(dateInput.value);
  if (parsed) {
    return parsed;
  }

  return String(dateInput.dataset.canonicalDate || "").trim();
}

function setDatePickerValue(dateInput, nativeDateInput, dateValue) {
  const safeDate = String(dateValue || "").trim();

  if (dateInput instanceof HTMLInputElement) {
    dateInput.value = safeDate ? formatDisplayDate(safeDate) : "";
    dateInput.dataset.canonicalDate = safeDate;
  }

  if (nativeDateInput instanceof HTMLInputElement) {
    nativeDateInput.value = safeDate;
  }
}

function normalizeDateTextValue(dateInput, nativeDateInput, preserveCurrentValue = false) {
  if (!(dateInput instanceof HTMLInputElement)) {
    return;
  }

  const rawValue = String(dateInput.value || "").trim();
  if (!rawValue) {
    setDatePickerValue(dateInput, nativeDateInput, "");
    return;
  }

  const parsedDate = parseDisplayDateValue(rawValue);
  if (!parsedDate) {
    const fallbackValue = preserveCurrentValue ? String(dateInput.dataset.canonicalDate || "").trim() : "";
    setDatePickerValue(dateInput, nativeDateInput, fallbackValue);
    return;
  }

  const minDateValue = formatInputDate(getMinimumDeadlineDate());
  const nextDateValue = parsedDate < minDateValue ? minDateValue : parsedDate;
  setDatePickerValue(dateInput, nativeDateInput, nextDateValue);
}

function refreshDeadlinePickers() {
  syncDeadlinePicker({
    dateInput: elements.taskDeadlineDate,
    nativeDateInput: elements.taskDeadlineNative,
    hourInput: elements.taskDeadlineHour,
    minuteInput: elements.taskDeadlineMinute,
    hourPrevButton: elements.taskDeadlineHourPrev,
    hourNextButton: elements.taskDeadlineHourNext,
    minutePrevButton: elements.taskDeadlineMinutePrev,
    minuteNextButton: elements.taskDeadlineMinuteNext,
    preserveCurrentValue: false,
  });

  syncDeadlinePicker({
    dateInput: elements.editTaskDeadlineDate,
    nativeDateInput: elements.editTaskDeadlineNative,
    hourInput: elements.editTaskDeadlineHour,
    minuteInput: elements.editTaskDeadlineMinute,
    hourPrevButton: elements.editTaskDeadlineHourPrev,
    hourNextButton: elements.editTaskDeadlineHourNext,
    minutePrevButton: elements.editTaskDeadlineMinutePrev,
    minuteNextButton: elements.editTaskDeadlineMinuteNext,
    preserveCurrentValue: true,
  });
}

function syncDeadlinePicker({
  dateInput,
  nativeDateInput,
  hourInput,
  minuteInput,
  hourPrevButton,
  hourNextButton,
  minutePrevButton,
  minuteNextButton,
  preserveCurrentValue = false,
}) {
  if (!(dateInput instanceof HTMLInputElement) || !(hourInput instanceof HTMLInputElement) || !(minuteInput instanceof HTMLInputElement)) {
    return;
  }

  const minDeadline = getMinimumDeadlineDate();
  const minDateValue = formatInputDate(minDeadline);
  const currentDate = getCanonicalDateValue(dateInput) || String(nativeDateInput?.value || "").trim();
  const currentCombined = combineDeadlineParts(currentDate, hourInput.value || "", minuteInput.value || "");

  if (nativeDateInput instanceof HTMLInputElement) {
    nativeDateInput.min = minDateValue;
  }

  if (!currentDate) {
    setDeadlineTimeValue({
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      timeValue: "",
      disableAll: true,
    });
    return;
  }

  if (currentDate < minDateValue) {
    if (preserveCurrentValue && currentCombined) {
      setDeadlineTimeValue({
        hourInput,
        minuteInput,
        hourPrevButton,
        hourNextButton,
        minutePrevButton,
        minuteNextButton,
        timeValue: `${hourInput.value}:${minuteInput.value}`,
        disableAll: true,
      });
      return;
    }

    setDeadlineTimeValue({
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      timeValue: "",
      disableAll: true,
    });
    return;
  }

  const bounds = getAvailableDeadlineBounds(currentDate, minDeadline);
  if (!bounds) {
    setDeadlineTimeValue({
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      timeValue: "",
      disableAll: true,
    });
    return;
  }

  const currentDateTime = parseDateTimeLocal(currentCombined);
  const isCurrentValid = currentDateTime && currentDateTime.getTime() >= bounds.min.getTime() && currentDateTime.getTime() <= bounds.max.getTime();

  const selectedDateTime = isCurrentValid
    ? currentDateTime
    : new Date(bounds.min.getTime());

  setDeadlineTimeValue({
    hourInput,
    minuteInput,
    hourPrevButton,
    hourNextButton,
    minutePrevButton,
    minuteNextButton,
    timeValue: formatTimeValue(selectedDateTime),
    disableAll: false,
    canDecreaseHour: selectedDateTime.getTime() - 60 * 60 * 1000 >= bounds.min.getTime(),
    canIncreaseHour: selectedDateTime.getTime() + 60 * 60 * 1000 <= bounds.max.getTime(),
    canDecreaseMinute: selectedDateTime.getTime() - DEADLINE_STEP_MINUTES * 60 * 1000 >= bounds.min.getTime(),
    canIncreaseMinute: selectedDateTime.getTime() + DEADLINE_STEP_MINUTES * 60 * 1000 <= bounds.max.getTime(),
  });
}

function shiftDeadlineTime({
  dateInput,
  nativeDateInput,
  hourInput,
  minuteInput,
  hourPrevButton,
  hourNextButton,
  minutePrevButton,
  minuteNextButton,
  deltaMinutes,
  preserveCurrentValue = false,
}) {
  const currentDate = getCanonicalDateValue(dateInput) || String(nativeDateInput?.value || "").trim();
  if (!currentDate) {
    return;
  }

  const minDeadline = getMinimumDeadlineDate();
  const bounds = getAvailableDeadlineBounds(currentDate, minDeadline);
  if (!bounds) {
    syncDeadlinePicker({
      dateInput,
      nativeDateInput,
      hourInput,
      minuteInput,
      hourPrevButton,
      hourNextButton,
      minutePrevButton,
      minuteNextButton,
      preserveCurrentValue,
    });
    return;
  }

  const currentValue = combineDeadlineParts(currentDate, hourInput?.value || "", minuteInput?.value || "");
  const currentDateTime = parseDateTimeLocal(currentValue) || new Date(bounds.min.getTime());
  let nextDateTime = new Date(currentDateTime.getTime() + deltaMinutes * 60 * 1000);

  if (nextDateTime.getTime() < bounds.min.getTime()) {
    nextDateTime = new Date(bounds.min.getTime());
  }
  if (nextDateTime.getTime() > bounds.max.getTime()) {
    nextDateTime = new Date(bounds.max.getTime());
  }

  setDeadlineTimeValue({
    hourInput,
    minuteInput,
    hourPrevButton,
    hourNextButton,
    minutePrevButton,
    minuteNextButton,
    timeValue: formatTimeValue(nextDateTime),
    disableAll: false,
    canDecreaseHour: nextDateTime.getTime() - 60 * 60 * 1000 >= bounds.min.getTime(),
    canIncreaseHour: nextDateTime.getTime() + 60 * 60 * 1000 <= bounds.max.getTime(),
    canDecreaseMinute: nextDateTime.getTime() - DEADLINE_STEP_MINUTES * 60 * 1000 >= bounds.min.getTime(),
    canIncreaseMinute: nextDateTime.getTime() + DEADLINE_STEP_MINUTES * 60 * 1000 <= bounds.max.getTime(),
  });
}

function clearDeadlinePicker(dateInput, nativeDateInput, hourInput, minuteInput, hourPrevButton, hourNextButton, minutePrevButton, minuteNextButton) {
  setDatePickerValue(dateInput, nativeDateInput, "");

  setDeadlineTimeValue({
    hourInput,
    minuteInput,
    hourPrevButton,
    hourNextButton,
    minutePrevButton,
    minuteNextButton,
    timeValue: "",
    disableAll: true,
  });
}

function setDeadlineTimeValue({
  hourInput,
  minuteInput,
  hourPrevButton,
  hourNextButton,
  minutePrevButton,
  minuteNextButton,
  timeValue = "",
  disableAll = false,
  canDecreaseHour = false,
  canIncreaseHour = false,
  canDecreaseMinute = false,
  canIncreaseMinute = false,
}) {
  if (!(hourInput instanceof HTMLInputElement) || !(minuteInput instanceof HTMLInputElement)) {
    return;
  }

  if (!timeValue) {
    hourInput.value = "";
    minuteInput.value = "";
    hourInput.disabled = true;
    minuteInput.disabled = true;
    hourPrevButton && (hourPrevButton.disabled = true);
    hourNextButton && (hourNextButton.disabled = true);
    minutePrevButton && (minutePrevButton.disabled = true);
    minuteNextButton && (minuteNextButton.disabled = true);
    return;
  }

  const [hourValue, minuteValue] = timeValue.split(":");
  hourInput.value = hourValue || "";
  minuteInput.value = minuteValue || "";
  hourInput.disabled = disableAll;
  minuteInput.disabled = disableAll;
  if (hourPrevButton) hourPrevButton.disabled = disableAll || !canDecreaseHour;
  if (hourNextButton) hourNextButton.disabled = disableAll || !canIncreaseHour;
  if (minutePrevButton) minutePrevButton.disabled = disableAll || !canDecreaseMinute;
  if (minuteNextButton) minuteNextButton.disabled = disableAll || !canIncreaseMinute;
}

function getAvailableDeadlineBounds(dateValue, minDeadline) {
  if (!dateValue) return null;

  const minDateValue = formatInputDate(minDeadline);
  if (dateValue < minDateValue) {
    return null;
  }

  const [year, month, day] = dateValue.split("-").map(Number);
  if (!year || !month || !day) {
    return null;
  }

  const dayStart = new Date(year, month - 1, day, 0, 0, 0, 0);
  const dayEnd = new Date(year, month - 1, day, 23, 55, 0, 0);

  return {
    min: dateValue === minDateValue ? new Date(minDeadline.getTime()) : dayStart,
    max: dayEnd,
  };
}

function getMinimumDeadlineDate() {
  const minDate = new Date(Date.now() + DEADLINE_OFFSET_MINUTES * 60 * 1000);
  minDate.setSeconds(0, 0);
  return roundDateUpToStep(minDate, DEADLINE_STEP_MINUTES);
}

function roundDateUpToStep(date, stepMinutes) {
  const stepMs = stepMinutes * 60 * 1000;
  return new Date(Math.ceil(date.getTime() / stepMs) * stepMs);
}

function formatInputDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatTimeValue(date) {
  const hour = String(date.getHours()).padStart(2, "0");
  const minute = String(date.getMinutes()).padStart(2, "0");
  return `${hour}:${minute}`;
}

function parseDateTimeLocal(value) {
  if (!value) return null;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date;
}

function combineDeadlineParts(dateValue, hourValue, minuteValue) {
  const safeDate = String(dateValue || "").trim();
  const safeHour = String(hourValue || "").trim();
  const safeMinute = String(minuteValue || "").trim();

  if (!safeDate || !safeHour || !safeMinute) {
    return null;
  }

  return `${safeDate}T${safeHour}:${safeMinute}:00`;
}

function splitDeadlineToPickerValue(value) {
  if (!value) {
    return { date: "", hour: "", minute: "" };
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return { date: "", hour: "", minute: "" };
  }

  return {
    date: formatInputDate(date),
    hour: String(date.getHours()).padStart(2, "0"),
    minute: String(date.getMinutes()).padStart(2, "0"),
  };
}

function validateTaskPatchPayload(payload) {
  if ("title" in payload) {
    if (!payload.title) {
      return "Название задачи не может быть пустым.";
    }

    if (payload.title.length > 80) {
      return "Название должно быть не длиннее 80 символов.";
    }
  }

  if ("description" in payload && payload.description.length > 500) {
    return "Описание должно быть не длиннее 500 символов.";
  }

  if ("deadline" in payload && payload.deadline && !isAtLeastThirtyMinutesAhead(payload.deadline)) {
    return "Дедлайн должен быть минимум на 30 минут позже текущего времени.";
  }

  return null;
}

function taskMatchesCurrentSelection(task) {
  const matchesStatus = state.statusFilter === "all"
    || normalizeStatus(task.status) === state.statusFilter;

  if (!matchesStatus) {
    return false;
  }

  const query = state.search.trim().toLowerCase();
  if (!query) {
    return true;
  }

  const title = String(task.title || "").toLowerCase();
  const description = String(task.description || "").toLowerCase();
  return title.includes(query) || description.includes(query);
}

function applyTasksStateChanges(nextTasks, nextAllTasks = state.allTasks) {
  state.tasks = sortTasks(nextTasks);
  state.allTasks = sortTasks(Array.isArray(nextAllTasks) ? nextAllTasks : []);
  updateStats();
  updateFilterCaption();
  updateSummary();
  renderTasks();
}

function mergeTaskIntoState(task) {
  const taskId = Number(task.id);

  const nextAllTasks = [...state.allTasks];
  const allTaskIndex = nextAllTasks.findIndex((item) => Number(item.id) === taskId);
  if (allTaskIndex >= 0) {
    nextAllTasks[allTaskIndex] = task;
  } else {
    nextAllTasks.unshift(task);
  }

  const nextTasks = [...state.tasks];
  const taskIndex = nextTasks.findIndex((item) => Number(item.id) === taskId);
  const matchesSelection = taskMatchesCurrentSelection(task);

  if (taskIndex >= 0 && !matchesSelection) {
    nextTasks.splice(taskIndex, 1);
    applyTasksStateChanges(nextTasks, nextAllTasks);
    return;
  }

  if (taskIndex >= 0) {
    nextTasks[taskIndex] = task;
    applyTasksStateChanges(nextTasks, nextAllTasks);
    return;
  }

  if (matchesSelection) {
    nextTasks.unshift(task);
  }

  applyTasksStateChanges(nextTasks, nextAllTasks);
}

function removeTaskFromState(taskId) {
  const nextTasks = state.tasks.filter((task) => Number(task.id) !== Number(taskId));
  const nextAllTasks = state.allTasks.filter((task) => Number(task.id) !== Number(taskId));
  applyTasksStateChanges(nextTasks, nextAllTasks);
}

function getTaskFromState(taskId) {
  return state.tasks.find((task) => Number(task.id) === Number(taskId))
    || state.allTasks.find((task) => Number(task.id) === Number(taskId))
    || null;
}

function getTaskFormPayload() {
  const title = document.getElementById("taskTitle")?.value.trim() || "";
  const description = document.getElementById("taskDescription")?.value.trim() || "";
  const priority = normalizePriority(document.getElementById("taskPriority")?.value || "medium");
  const deadline = combineDeadlineParts(
    getCanonicalDateValue(elements.taskDeadlineDate),
    elements.taskDeadlineHour?.value || "",
    elements.taskDeadlineMinute?.value || "",
  );

  return { title, description, priority, deadline };
}

function validateTaskPayload(payload) {
  if (!payload.title) {
    return "Название задачи не может быть пустым.";
  }

  if (payload.title.length > 80) {
    return "Название должно быть не длиннее 80 символов.";
  }

  if (payload.description.length > 500) {
    return "Описание должно быть не длиннее 500 символов.";
  }

  if (payload.deadline && !isAtLeastThirtyMinutesAhead(payload.deadline)) {
    return "Дедлайн должен быть минимум на 30 минут позже текущего времени.";
  }

  return null;
}

function applyAuthorizedSession(token, username, { successMessage = "Вход выполнен успешно." } = {}) {
  state.token = token || "";
  state.username = username || "";

  localStorage.setItem("token", state.token);
  localStorage.setItem("username", state.username);

  elements.loginForm?.reset();
  clearAuthInlineErrors("login");
  clearAuthInlineErrors("register");
  setAuthMode("login");
  showMessage(successMessage, "success");
  updateView();
  clearInlineMessage(elements.loginUsername, elements.loginUsernameError);
  clearInlineMessage(elements.loginPassword, elements.loginPasswordError);
  if (elements.loginUsername) elements.loginUsername.dataset.touched = "false";
  if (elements.loginPassword) elements.loginPassword.dataset.touched = "false";
  state.loginCredentialsErrorActive = false;
}

async function registerUser(event) {
  event.preventDefault();
  clearMessage();

  if (!validateAuthFields("register")) {
    return;
  }

  const username = elements.registerUsername?.value.trim() || "";
  const password = elements.registerPassword?.value.trim() || "";

  setButtonBusy(elements.registerSubmitBtn, true, "Создаём аккаунт...");

  try {
    const response = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify({ username, password }),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      if (!mapServerMessageToField(data.error || data.message, "register")) {
        showMessage(data.error || data.message || "Не удалось зарегистрироваться.", "error");
      }
      return;
    }

    const loginResponse = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify({ username, password }),
    });

    const loginData = await safeReadJson(loginResponse);

    if (!loginResponse.ok || !loginData.access_token) {
      elements.registerForm?.reset();
      clearAuthInlineErrors("register");
      const loginField = elements.loginUsername;
      if (loginField) {
        loginField.value = username;
        loginField.dataset.touched = "false";
      }

      clearInlineMessage(elements.loginUsername, elements.loginUsernameError);
      setAuthMode("login");
      showMessage("Аккаунт создан, но автологин не выполнился. Войди вручную.", "warning");
      return;
    }

    elements.registerForm?.reset();
    applyAuthorizedSession(loginData.access_token, username, {
      successMessage: "Аккаунт создан и вход выполнен автоматически.",
    });
  } catch (_error) {
    showMessage("Сервис регистрации недоступен.", "error");
  } finally {
    setButtonBusy(elements.registerSubmitBtn, false);
  }
}

async function loginUser(event) {
  event.preventDefault();
  clearMessage();

  if (!validateAuthFields("login")) {
    return;
  }

  const username = elements.loginUsername?.value.trim() || "";
  const password = elements.loginPassword?.value.trim() || "";

  setButtonBusy(elements.loginSubmitBtn, true, "Входим...");

  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify({ username, password }),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      if (!mapServerMessageToField(data.error || data.message, "login")) {
        showMessage(data.error || data.message || "Не удалось войти.", "error");
      }
      return;
    }

    applyAuthorizedSession(data.access_token || "", username, {
      successMessage: "Вход выполнен успешно.",
    });
  } catch (_error) {
    showMessage("Сервис входа недоступен.", "error");
  } finally {
    setButtonBusy(elements.loginSubmitBtn, false);
  }
}

async function loadTasks(options = {}) {
  const { preserveMessage = false } = options;

  if (!state.token || state.isLoading) return;

  if (!preserveMessage) {
    clearMessage();
  }

  state.isLoading = true;
  setLoadingState(true);

  try {
    const filteredResponsePromise = fetch(buildTasksUrl(), {
      method: "GET",
      headers: getAuthHeaders(false),
    });

    const shouldLoadGlobalStats = state.statusFilter !== "all" || Boolean(state.search);
    const allTasksResponsePromise = shouldLoadGlobalStats
      ? fetch(`${API_BASE}/tasks`, {
          method: "GET",
          headers: getAuthHeaders(false),
        })
      : null;

    const filteredResponse = await filteredResponsePromise;
    const filteredData = await safeReadJson(filteredResponse);

    if (!filteredResponse.ok) {
      showMessage(filteredData.error || filteredData.message || "Не удалось загрузить задачи.", "error");
      return;
    }

    let allTasksData = filteredData;

    if (allTasksResponsePromise) {
      const allTasksResponse = await allTasksResponsePromise;
      allTasksData = await safeReadJson(allTasksResponse);

      if (!allTasksResponse.ok) {
        showMessage(allTasksData.error || allTasksData.message || "Не удалось загрузить общую статистику.", "error");
        return;
      }
    }

    applyTasksStateChanges(
      Array.isArray(filteredData) ? filteredData : [],
      Array.isArray(allTasksData) ? allTasksData : [],
    );
  } catch (_error) {
    applyTasksStateChanges([], []);
    showMessage("Не удалось подключиться к Tasks API.", "warning");
  } finally {
    state.isLoading = false;
    setLoadingState(false);
  }
}

function setLoadingState(isLoading) {
  setButtonBusy(elements.reloadTasksBtn, isLoading, "Обновляем...");
  elements.applyFiltersBtn?.toggleAttribute("disabled", isLoading);
  elements.resetFiltersBtn?.toggleAttribute("disabled", isLoading);

  if (elements.tasksSummary) {
    elements.tasksSummary.classList.toggle("results-summary--loading", isLoading && !state.tasks.length);
    if (isLoading && !state.tasks.length) {
      elements.tasksSummary.textContent = "Загружаем задачи…";
    }
  }

  if (!elements.tasksList) return;

  elements.tasksList.classList.toggle("tasks-list--loading", isLoading);

  if (isLoading && !state.tasks.length) {
    elements.tasksList.innerHTML = renderTaskSkeletons(3);
  }
}

function renderTaskSkeletons(count = 3) {
  return Array.from({ length: count }, () => `
    <article class="task-card task-card-skeleton" aria-hidden="true">
      <div class="task-card__header">
        <div class="task-card__identity skeleton-stack">
          <span class="skeleton skeleton-line skeleton-line--kicker"></span>
          <span class="skeleton skeleton-line skeleton-line--title"></span>
        </div>
        <div class="task-meta skeleton-meta">
          <span class="skeleton skeleton-pill"></span>
          <span class="skeleton skeleton-pill"></span>
          <span class="skeleton skeleton-pill"></span>
        </div>
      </div>
      <div class="skeleton-stack task-card-skeleton__body">
        <span class="skeleton skeleton-line skeleton-line--body"></span>
        <span class="skeleton skeleton-line skeleton-line--body-short"></span>
      </div>
      <div class="task-details">
        <div class="task-detail task-detail--skeleton">
          <span class="skeleton skeleton-line skeleton-line--label"></span>
          <span class="skeleton skeleton-line skeleton-line--value"></span>
        </div>
        <div class="task-detail task-detail--skeleton">
          <span class="skeleton skeleton-line skeleton-line--label"></span>
          <span class="skeleton skeleton-line skeleton-line--value"></span>
        </div>
      </div>
      <div class="task-card__footer">
        <div class="task-actions task-actions--status skeleton-actions">
          <span class="skeleton skeleton-button"></span>
          <span class="skeleton skeleton-button"></span>
          <span class="skeleton skeleton-button"></span>
        </div>
        <div class="task-actions skeleton-actions">
          <span class="skeleton skeleton-button skeleton-button--wide"></span>
          <span class="skeleton skeleton-button"></span>
        </div>
      </div>
    </article>
  `).join("");
}

function buildTasksUrl() {
  const params = new URLSearchParams();

  if (state.statusFilter !== "all") {
    params.set("status", state.statusFilter);
  }

  if (state.search) {
    params.set("search", state.search);
  }

  const query = params.toString();
  return query ? `${API_BASE}/tasks?${query}` : `${API_BASE}/tasks`;
}

function sortTasks(tasks) {
  const priorityOrder = { high: 3, medium: 2, low: 1 };

  return [...tasks].sort((first, second) => {
    const firstDeadline = first?.deadline ? new Date(first.deadline).getTime() : Number.POSITIVE_INFINITY;
    const secondDeadline = second?.deadline ? new Date(second.deadline).getTime() : Number.POSITIVE_INFINITY;
    const firstDate = first?.created_at ? new Date(first.created_at).getTime() : 0;
    const secondDate = second?.created_at ? new Date(second.created_at).getTime() : 0;
    const firstPriority = priorityOrder[normalizePriority(first?.priority)] || 0;
    const secondPriority = priorityOrder[normalizePriority(second?.priority)] || 0;

    if (state.sortBy === "priority_desc") {
      if (firstPriority !== secondPriority) {
        return secondPriority - firstPriority;
      }

      if (firstDeadline !== secondDeadline) {
        return firstDeadline - secondDeadline;
      }

      return secondDate - firstDate;
    }

    if (state.sortBy === "created_desc") {
      if (firstDate !== secondDate) {
        return secondDate - firstDate;
      }

      if (firstPriority !== secondPriority) {
        return secondPriority - firstPriority;
      }

      return firstDeadline - secondDeadline;
    }

    if (firstDeadline !== secondDeadline) {
      return firstDeadline - secondDeadline;
    }

    if (firstPriority !== secondPriority) {
      return secondPriority - firstPriority;
    }

    return secondDate - firstDate;
  });
}

function renderTasks() {
  if (!elements.tasksList) return;

  if (!state.tasks.length) {
    elements.tasksList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state__icon">⌁</div>
        <div class="empty-state__title">Пока нет задач</div>
        <div class="empty-state__text">Создай первую задачу, измени фильтр или попробуй другой поисковый запрос.</div>
      </div>
    `;
    return;
  }

  elements.tasksList.innerHTML = state.tasks.map((task) => {
    const status = normalizeStatus(task.status);
    const priority = normalizePriority(task.priority);
    const deadlineState = getDeadlineState(task.deadline);
    const actionState = getTaskAction(task.id);
    const isCardBusy = Boolean(actionState);
    const editLabel = actionState?.type === "edit" ? "Открываем..." : "Редактировать";
    const deleteLabel = actionState?.type === "delete" ? "Удаляем..." : "Удалить";

    return `
      <article class="task-card ${isCardBusy ? "task-card--busy" : ""}" data-task-id="${task.id}">
        <div class="task-card__header">
          <div class="task-card__identity">
            <div class="task-card__kicker">Задача #${task.id ?? "—"}</div>
            <h3 class="task-title">${escapeHtml(task.title || "Без названия")}</h3>
          </div>
          <div class="task-meta">
            <span class="badge badge-status status-${status}">${formatStatus(status)}</span>
            <span class="badge badge-priority priority-${priority}">${formatPriority(priority)}</span>
            ${renderDeadlineBadge(deadlineState)}
          </div>
        </div>

        <p class="task-description">${escapeHtml(task.description || "Без описания")}</p>

        <div class="task-details">
          <div class="task-detail">
            <span class="task-detail__label">Дедлайн</span>
            <span class="task-detail__value ${deadlineState.className}">${formatDate(task.deadline)}</span>
          </div>
          <div class="task-detail">
            <span class="task-detail__label">Создано</span>
            <span class="task-detail__value">${formatDate(task.created_at)}</span>
          </div>
        </div>

        <div class="task-card__footer">
          <div class="task-actions task-actions--status">
            ${renderStatusButtons(task.id, status)}
          </div>

          <div class="task-actions">
            <button type="button" class="action-btn action-btn-edit ${actionState?.type === "edit" ? "is-busy" : ""}" data-action="edit" data-id="${task.id}" ${isCardBusy ? "disabled" : ""}>
              ${editLabel}
            </button>
            <button type="button" class="action-btn action-btn-danger ${actionState?.type === "delete" ? "is-busy" : ""}" data-action="delete" data-id="${task.id}" ${isCardBusy ? "disabled" : ""}>
              ${deleteLabel}
            </button>
          </div>
        </div>
      </article>
    `;
  }).join("");
}

function renderDeadlineBadge(deadlineState) {
  if (!deadlineState.label) {
    return '<span class="badge badge-deadline badge-deadline-muted">Без дедлайна</span>';
  }

  return `<span class="badge badge-deadline ${deadlineState.badgeClass}">${deadlineState.label}</span>`;
}

function renderStatusButtons(taskId, currentStatus) {
  const variants = [
    { value: "new", label: "Новая" },
    { value: "in_progress", label: "В работе" },
    { value: "done", label: "Готово" },
  ];
  const actionState = getTaskAction(taskId);
  const isBusy = Boolean(actionState);

  return variants.map((item) => {
    const isCurrent = item.value === currentStatus;
    const isPendingTarget = actionState?.type === "status" && actionState.status === item.value;
    const label = isPendingTarget ? "Сохраняем..." : item.label;

    return `
      <button
        type="button"
        class="action-btn ${isCurrent ? "is-current" : ""} ${isPendingTarget ? "is-busy" : ""}"
        data-action="status"
        data-id="${taskId}"
        data-status="${item.value}"
        ${isCurrent ? 'aria-current="true"' : ""}
        ${isBusy ? "disabled" : ""}
      >
        ${label}
      </button>
    `;
  }).join("");
}

async function createTask(event) {
  event.preventDefault();
  clearMessage();

  if (!validateTaskFields("create")) {
    return;
  }

  const payload = getTaskFormPayload();
  setButtonBusy(elements.taskSubmitBtn, true, "Добавляем...");

  try {
    const response = await fetch(`${API_BASE}/tasks`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify(payload),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      if (!mapServerMessageToField(data.error || data.message, "create")) {
        showMessage(data.error || data.message || "Не удалось создать задачу.", "error");
      }
      return;
    }

    elements.taskForm?.reset();
    const priorityField = document.getElementById("taskPriority");
    if (priorityField) {
      priorityField.value = "medium";
      refreshCustomSelect(priorityField);
    }

    clearDeadlinePicker(elements.taskDeadlineDate, elements.taskDeadlineNative, elements.taskDeadlineHour, elements.taskDeadlineMinute, elements.taskDeadlineHourPrev, elements.taskDeadlineHourNext, elements.taskDeadlineMinutePrev, elements.taskDeadlineMinuteNext);
    clearTaskFormInlineState("create");

    showMessage("Задача добавлена.", "success");
    mergeTaskIntoState(data);
  } catch (_error) {
    showMessage("Не удалось создать задачу.", "error");
  } finally {
    setButtonBusy(elements.taskSubmitBtn, false);
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
    requestDeleteTask(taskId);
  }

  if (action === "edit") {
    openEditModal(taskId);
  }
}

function requestDeleteTask(taskId) {
  const task = getTaskFromState(taskId);
  state.pendingDeleteTaskId = taskId;

  safeSetText(
    elements.deleteModalTaskText,
    task?.title ? `Задача: ${task.title}` : `Задача #${taskId}`
  );

  elements.deleteModal?.classList.remove("hidden");
  elements.deleteModal?.setAttribute("aria-hidden", "false");
  document.body.classList.add("body-lock");
  elements.confirmDeleteBtn?.focus();
}

function closeDeleteModal() {
  elements.deleteModal?.classList.add("hidden");
  elements.deleteModal?.setAttribute("aria-hidden", "true");
  safeSetText(elements.deleteModalTaskText, "—");
  state.pendingDeleteTaskId = null;

  if (elements.editModal?.classList.contains("hidden")) {
    document.body.classList.remove("body-lock");
  }
}

function handleDeleteModalClick(event) {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  if (target.dataset.closeDeleteModal === "true") {
    closeDeleteModal();
  }
}

async function confirmDeleteTask() {
  const taskId = Number(state.pendingDeleteTaskId || 0);
  if (!taskId) {
    closeDeleteModal();
    return;
  }

  await deleteTask(taskId);
}

async function updateTaskStatus(taskId, status) {
  clearMessage();
  setTaskAction(taskId, { type: "status", status });

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
    mergeTaskIntoState(data);
  } catch (_error) {
    showMessage("Не удалось изменить статус.", "error");
  } finally {
    setTaskAction(taskId, null);
  }
}

async function deleteTask(taskId) {
  clearMessage();
  setTaskAction(taskId, { type: "delete" });
  setButtonBusy(elements.confirmDeleteBtn, true, "Удаляем...");

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

    closeDeleteModal();
    showMessage("Задача удалена.", "success");
    removeTaskFromState(taskId);
  } catch (_error) {
    showMessage("Не удалось удалить задачу.", "error");
  } finally {
    setButtonBusy(elements.confirmDeleteBtn, false);
    setTaskAction(taskId, null);
  }
}

async function openEditModal(taskId) {
  clearMessage();
  setTaskAction(taskId, { type: "edit" });

  try {
    let data = getTaskFromState(taskId);

    if (!data) {
      const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: "GET",
        headers: getAuthHeaders(false),
      });

      data = await safeReadJson(response);

      if (!response.ok) {
        showMessage(data.error || data.message || "Не удалось получить задачу.", "error");
        return;
      }
    }

    if (!elements.editTaskId || !elements.editTaskTitle || !elements.editTaskDescription || !elements.editTaskPriority || !elements.editTaskDeadlineDate || !elements.editTaskDeadlineHour || !elements.editTaskDeadlineMinute) {
      showMessage("Форма редактирования не инициализирована.", "error");
      return;
    }

    const deadlineParts = splitDeadlineToPickerValue(data.deadline);

    state.editingTaskOriginal = {
      id: data.id,
      title: data.title || "",
      description: data.description || "",
      priority: normalizePriority(data.priority),
      deadline: combineDeadlineParts(deadlineParts.date, deadlineParts.hour, deadlineParts.minute),
    };

    elements.editTaskId.value = String(data.id || "");
    elements.editTaskTitle.value = state.editingTaskOriginal.title;
    elements.editTaskDescription.value = state.editingTaskOriginal.description;
    clearTaskFormInlineState("edit");
    elements.editTaskPriority.value = state.editingTaskOriginal.priority;
    refreshCustomSelect(elements.editTaskPriority);
    setDatePickerValue(elements.editTaskDeadlineDate, elements.editTaskDeadlineNative, deadlineParts.date);
    syncDeadlinePicker({
      dateInput: elements.editTaskDeadlineDate,
      nativeDateInput: elements.editTaskDeadlineNative,
      hourInput: elements.editTaskDeadlineHour,
      minuteInput: elements.editTaskDeadlineMinute,
      hourPrevButton: elements.editTaskDeadlineHourPrev,
      hourNextButton: elements.editTaskDeadlineHourNext,
      minutePrevButton: elements.editTaskDeadlineMinutePrev,
      minuteNextButton: elements.editTaskDeadlineMinuteNext,
      preserveCurrentValue: true,
    });
    elements.editTaskDeadlineHour.value = deadlineParts.hour;
    elements.editTaskDeadlineMinute.value = deadlineParts.minute;
    syncDeadlinePicker({
      dateInput: elements.editTaskDeadlineDate,
      nativeDateInput: elements.editTaskDeadlineNative,
      hourInput: elements.editTaskDeadlineHour,
      minuteInput: elements.editTaskDeadlineMinute,
      hourPrevButton: elements.editTaskDeadlineHourPrev,
      hourNextButton: elements.editTaskDeadlineHourNext,
      minutePrevButton: elements.editTaskDeadlineMinutePrev,
      minuteNextButton: elements.editTaskDeadlineMinuteNext,
      preserveCurrentValue: true,
    });

    elements.editModal?.classList.remove("hidden");
    elements.editModal?.setAttribute("aria-hidden", "false");
    document.body.classList.add("body-lock");
    elements.editTaskTitle.focus();
  } catch (_error) {
    showMessage("Не удалось открыть редактирование задачи.", "error");
  } finally {
    setTaskAction(taskId, null);
  }
}

function closeEditModal() {
  elements.editModal?.classList.add("hidden");
  elements.editModal?.setAttribute("aria-hidden", "true");
  elements.editTaskForm?.reset();
  clearDeadlinePicker(elements.editTaskDeadlineDate, elements.editTaskDeadlineNative, elements.editTaskDeadlineHour, elements.editTaskDeadlineMinute, elements.editTaskDeadlineHourPrev, elements.editTaskDeadlineHourNext, elements.editTaskDeadlineMinutePrev, elements.editTaskDeadlineMinuteNext);
  clearTaskFormInlineState("edit");
  state.editingTaskOriginal = null;

  if (elements.deleteModal?.classList.contains("hidden")) {
    document.body.classList.remove("body-lock");
  }
}

function handleModalClick(event) {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  if (target.dataset.closeModal === "true") {
    closeEditModal();
  }
}

async function submitTaskEdit(event) {
  event.preventDefault();
  clearMessage();

  const taskId = Number(elements.editTaskId?.value || 0);
  if (!taskId) {
    showMessage("Не удалось определить задачу для редактирования.", "error");
    return;
  }

  if (!validateTaskFields("edit")) {
    return;
  }

  const original = state.editingTaskOriginal || {
    title: "",
    description: "",
    priority: "medium",
    deadline: null,
  };

  const currentValues = {
    title: elements.editTaskTitle?.value.trim() || "",
    description: elements.editTaskDescription?.value.trim() || "",
    priority: normalizePriority(elements.editTaskPriority?.value || "medium"),
    deadline: combineDeadlineParts(
      getCanonicalDateValue(elements.editTaskDeadlineDate),
      elements.editTaskDeadlineHour?.value || "",
      elements.editTaskDeadlineMinute?.value || "",
    ),
  };

  const payload = {};

  if (currentValues.title !== original.title) {
    payload.title = currentValues.title;
  }
  if (currentValues.description !== original.description) {
    payload.description = currentValues.description;
  }
  if (currentValues.priority !== original.priority) {
    payload.priority = currentValues.priority;
  }
  if (currentValues.deadline !== original.deadline) {
    payload.deadline = currentValues.deadline;
  }

  if (!Object.keys(payload).length) {
    closeEditModal();
    showMessage("Изменений нет.", "warning");
    return;
  }

  setButtonBusy(elements.editTaskSubmitBtn, true, "Сохраняем...");

  try {
    const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: "PATCH",
      headers: getAuthHeaders(true),
      body: JSON.stringify(payload),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      if (!mapServerMessageToField(data.error || data.message, "edit")) {
        showMessage(data.error || data.message || "Не удалось сохранить изменения.", "error");
      }
      return;
    }

    closeEditModal();
    showMessage("Задача обновлена.", "success");
    mergeTaskIntoState(data);
  } catch (_error) {
    showMessage("Не удалось сохранить изменения.", "error");
  } finally {
    setButtonBusy(elements.editTaskSubmitBtn, false);
  }
}

function applyFilters() {
  state.search = elements.searchInput?.value.trim() || "";
  state.statusFilter = elements.statusFilterSelect?.value || "all";
  state.sortBy = elements.sortSelect?.value || "deadline_asc";
  localStorage.setItem("sortBy", state.sortBy);
  updateFilterCaption();
  loadTasks();
}

function resetFilters() {
  state.search = "";
  state.statusFilter = "all";
  state.sortBy = "deadline_asc";
  localStorage.setItem("sortBy", state.sortBy);
  syncFilterControls();
  updateFilterCaption();
  loadTasks();
}

function logout() {
  state.token = "";
  state.username = "";
  state.tasks = [];
  state.allTasks = [];
  state.statusFilter = "all";
  state.search = "";
  state.sortBy = "deadline_asc";
  state.editingTaskOriginal = null;
  taskActionState.clear();

  localStorage.removeItem("token");
  localStorage.removeItem("username");
  localStorage.removeItem("sortBy");

  syncFilterControls();
  closeEditModal();
  closeDeleteModal();
  clearTaskFormInlineState("create");
  clearTaskFormInlineState("edit");
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


function isAtLeastThirtyMinutesAhead(value) {
  const deadlineDate = new Date(value);
  if (Number.isNaN(deadlineDate.getTime())) return false;

  const now = new Date();
  const minDate = new Date(now.getTime() + 30 * 60 * 1000);
  return deadlineDate.getTime() >= minDate.getTime();
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

function formatFilterLabel(status) {
  if (status === "new") return "Новые";
  if (status === "in_progress") return "В работе";
  if (status === "done") return "Готово";
  return "Все задачи";
}

function formatSortLabel(sortBy) {
  if (sortBy === "priority_desc") return "Высокий приоритет";
  if (sortBy === "created_desc") return "Сначала новые";
  return "Ближайший дедлайн";
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

function getDeadlineState(value) {
  if (!value) {
    return {
      label: "",
      className: "",
      badgeClass: "badge-deadline-muted",
    };
  }

  const deadlineDate = new Date(value);
  if (Number.isNaN(deadlineDate.getTime())) {
    return {
      label: "Ошибка даты",
      className: "task-detail__value--danger",
      badgeClass: "badge-deadline-danger",
    };
  }

  const diffMs = deadlineDate.getTime() - Date.now();
  const diffHours = diffMs / (1000 * 60 * 60);

  if (diffHours <= 24) {
    return {
      label: "Скоро",
      className: "task-detail__value--warning",
      badgeClass: "badge-deadline-warning",
    };
  }

  return {
    label: "Планово",
    className: "task-detail__value--ok",
    badgeClass: "badge-deadline-ok",
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

applyTheme(state.theme);
refreshDeadlinePickers();
syncFilterControls();
updateView();
