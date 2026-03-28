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
  authMode: "login",
  isLoading: false,
  editingTaskOriginal: null,
  messageTimerId: null,
};

const elements = {
  authSection: document.getElementById("authSection"),
  appSection: document.getElementById("appSection"),
  messageBox: document.getElementById("messageBox"),
  userText: document.getElementById("userText"),
  authStatusText: document.getElementById("authStatusText"),
  activeFilterText: document.getElementById("activeFilterText"),
  totalCount: document.getElementById("totalCount"),
  newCount: document.getElementById("newCount"),
  progressCount: document.getElementById("progressCount"),
  doneCount: document.getElementById("doneCount"),
  tasksSummary: document.getElementById("tasksSummary"),
  tasksList: document.getElementById("tasksList"),
  logoutBtn: document.getElementById("logoutBtn"),
  reloadTasksBtn: document.getElementById("reloadTasksBtn"),
  loginForm: document.getElementById("loginForm"),
  registerForm: document.getElementById("registerForm"),
  taskForm: document.getElementById("taskForm"),
  authModeTriggers: document.querySelectorAll("[data-auth-mode]"),
  authForms: document.querySelectorAll("[data-form-mode]"),
  searchInput: document.getElementById("searchInput"),
  statusFilterSelect: document.getElementById("statusFilterSelect"),
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
  }
});

elements.authModeTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => {
    const nextMode = trigger.dataset.authMode;
    if (!nextMode) return;
    setAuthMode(nextMode);
  });
});

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
  safeSetText(elements.activeFilterText, `${statusLabel}${searchLabel}`);
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
  }
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
    normalizeDateTextValue(dateInput, nativeDateInput, preserveCurrentValue);
    sync();
  });

  nativeDateInput?.addEventListener("change", () => {
    setDatePickerValue(dateInput, nativeDateInput, nativeDateInput.value || "");
    sync();
  });

  dateTriggerButton?.addEventListener("click", () => {
    if (!(nativeDateInput instanceof HTMLInputElement)) {
      return;
    }

    const minDateValue = formatInputDate(getMinimumDeadlineDate());
    nativeDateInput.min = minDateValue;
    if (!nativeDateInput.value) {
      nativeDateInput.value = getCanonicalDateValue(dateInput) || minDateValue;
    }

    if (typeof nativeDateInput.showPicker === "function") {
      nativeDateInput.showPicker();
      return;
    }

    nativeDateInput.focus();
    nativeDateInput.click();
  });

  hourPrevButton?.addEventListener("click", () => {
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
    clearDeadlinePicker(dateInput, nativeDateInput, hourInput, minuteInput, hourPrevButton, hourNextButton, minutePrevButton, minuteNextButton);
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
  } catch (_error) {
    showMessage("Сервис входа недоступен.", "error");
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
  elements.reloadTasksBtn?.toggleAttribute("disabled", isLoading);
  elements.applyFiltersBtn?.toggleAttribute("disabled", isLoading);
  elements.resetFiltersBtn?.toggleAttribute("disabled", isLoading);

  if (!elements.tasksList) return;

  if (isLoading && !state.tasks.length) {
    elements.tasksList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state__icon">⋯</div>
        <div class="empty-state__title">Загрузка задач</div>
        <div class="empty-state__text">Подтягиваем актуальную выборку с сервера.</div>
      </div>
    `;
  }
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
  return [...tasks].sort((first, second) => {
    const firstDeadline = first?.deadline ? new Date(first.deadline).getTime() : Number.POSITIVE_INFINITY;
    const secondDeadline = second?.deadline ? new Date(second.deadline).getTime() : Number.POSITIVE_INFINITY;

    if (firstDeadline !== secondDeadline) {
      return firstDeadline - secondDeadline;
    }

    const firstDate = first?.created_at ? new Date(first.created_at).getTime() : 0;
    const secondDate = second?.created_at ? new Date(second.created_at).getTime() : 0;
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
            <button type="button" class="action-btn action-btn-edit" data-action="edit" data-id="${task.id}">
              Редактировать
            </button>
            <button type="button" class="action-btn action-btn-danger" data-action="delete" data-id="${task.id}">
              Удалить
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

  const payload = getTaskFormPayload();
  const validationError = validateTaskPayload(payload);

  if (validationError) {
    showMessage(validationError, "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/tasks`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify(payload),
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

    clearDeadlinePicker(elements.taskDeadlineDate, elements.taskDeadlineNative, elements.taskDeadlineHour, elements.taskDeadlineMinute, elements.taskDeadlineHourPrev, elements.taskDeadlineHourNext, elements.taskDeadlineMinutePrev, elements.taskDeadlineMinuteNext);

    showMessage("Задача добавлена.", "success");
    mergeTaskIntoState(data);
  } catch (_error) {
    showMessage("Не удалось создать задачу.", "error");
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

  if (action === "edit") {
    openEditModal(taskId);
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
    mergeTaskIntoState(data);
  } catch (_error) {
    showMessage("Не удалось изменить статус.", "error");
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
    removeTaskFromState(taskId);
  } catch (_error) {
    showMessage("Не удалось удалить задачу.", "error");
  }
}

async function openEditModal(taskId) {
  clearMessage();

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
    elements.editTaskPriority.value = state.editingTaskOriginal.priority;
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
  }
}

function closeEditModal() {
  elements.editModal?.classList.add("hidden");
  elements.editModal?.setAttribute("aria-hidden", "true");
  elements.editTaskForm?.reset();
  clearDeadlinePicker(elements.editTaskDeadlineDate, elements.editTaskDeadlineNative, elements.editTaskDeadlineHour, elements.editTaskDeadlineMinute, elements.editTaskDeadlineHourPrev, elements.editTaskDeadlineHourNext, elements.editTaskDeadlineMinutePrev, elements.editTaskDeadlineMinuteNext);
  state.editingTaskOriginal = null;
  document.body.classList.remove("body-lock");
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

  const validationError = validateTaskPatchPayload(payload);
  if (validationError) {
    showMessage(validationError, "error");
    return;
  }

  if (!Object.keys(payload).length) {
    closeEditModal();
    showMessage("Изменений нет.", "warning");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: "PATCH",
      headers: getAuthHeaders(true),
      body: JSON.stringify(payload),
    });

    const data = await safeReadJson(response);

    if (!response.ok) {
      showMessage(data.error || data.message || "Не удалось сохранить изменения.", "error");
      return;
    }

    closeEditModal();
    showMessage("Задача обновлена.", "success");
    mergeTaskIntoState(data);
  } catch (_error) {
    showMessage("Не удалось сохранить изменения.", "error");
  }
}

function applyFilters() {
  state.search = elements.searchInput?.value.trim() || "";
  state.statusFilter = elements.statusFilterSelect?.value || "all";
  updateFilterCaption();
  loadTasks();
}

function resetFilters() {
  state.search = "";
  state.statusFilter = "all";
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
  state.editingTaskOriginal = null;

  localStorage.removeItem("token");
  localStorage.removeItem("username");

  syncFilterControls();
  closeEditModal();
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

refreshDeadlinePickers();
syncFilterControls();
updateView();
