const taskList = document.getElementById("taskList");
const modal = document.getElementById("taskModal");
const addTaskButton = document.getElementById("addTaskButton");
const closeModal = document.getElementById("closeModal");
const taskForm = document.getElementById("taskForm");
const themeToggle = document.getElementById("themeToggle");

function updateDate() {
    const today = new Date();
    document.getElementById("todayDate").textContent =
        today.toLocaleDateString("en-US", {
            weekday: "long", month: "long", day: "numeric", year: "numeric"
        });

    const hour = today.getHours();
    let greeting = "Good evening!";
    if (hour < 12) greeting = "Good morning!";
    else if (hour < 18) greeting = "Good afternoon!";
    document.getElementById("greeting").textContent = greeting;
}

async function loadTasks() {
    const response = await fetch("/api/tasks");
    const tasks = await response.json();
    taskList.innerHTML = "";

    if (tasks.length === 0) {
        taskList.innerHTML = `
            <div class="empty-state">
                No tasks scheduled for today.<br><br>
                Enjoy the rare moment of peace.
            </div>`;
        updateStats();
        return;
    }

    tasks.forEach(task => {
        const card = document.createElement("div");
        card.className = "task-card";
        card.innerHTML = `
            <div class="task-checkbox ${task.completed ? "completed" : ""}"
                 onclick="toggleTask(${task.id})">
                ${task.completed ? "✓" : ""}
            </div>
            <div class="task-info">
                <div class="task-name">${escapeHtml(task.name)}</div>
                <div class="task-description">${escapeHtml(task.description || "")}</div>
            </div>
            <div class="streak">🔥 ${task.streak}</div>`;
        taskList.appendChild(card);
    });

    updateStats();
}

async function toggleTask(taskId) {
    await fetch(`/api/tasks/${taskId}/complete`, { method: "POST" });
    loadTasks();
}

async function updateStats() {
    const response = await fetch("/api/stats");
    const stats = await response.json();

    document.getElementById("completedCount").textContent = stats.completed;
    document.getElementById("totalCount").textContent = stats.total;
    document.getElementById("percentage").textContent = `${stats.percentage}%`;
    document.getElementById("progressFill").style.width = `${stats.percentage}%`;
    document.querySelector(".progress-bar").setAttribute("aria-valuenow", stats.percentage);
    document.getElementById("overallStreak").textContent =
        `${stats.streak} ${stats.streak === 1 ? "day" : "days"} streak`;
    renderWeek(stats.week, stats.today);
}

function renderWeek(days, today) {
    const weekGrid = document.getElementById("weekGrid");

    weekGrid.innerHTML = days.map(day => {
        const future = day.date > today;
        let status = "Rest day";
        let marker = "-";
        if (day.total > 0 && day.completed === day.total) {
            status = "Complete";
            marker = "✓";
        } else if (day.total > 0 && future) {
            status = `${day.total} scheduled`;
            marker = day.total;
        } else if (day.total > 0) {
            status = `${day.completed} of ${day.total} done`;
            marker = day.completed;
        }

        return `<div class="day-card ${day.date === today ? "today" : ""}" title="${status}">
            <span>${escapeHtml(day.day)}</span>
            <strong>${marker}</strong>
            <small>${day.date.slice(8)}</small>
        </div>`;
    }).join("");
}

addTaskButton.addEventListener("click", () => modal.classList.remove("hidden"));
closeModal.addEventListener("click", () => modal.classList.add("hidden"));
modal.addEventListener("click", event => {
    if (event.target === modal) modal.classList.add("hidden");
});

taskForm.addEventListener("submit", async event => {
    event.preventDefault();

    const name = document.getElementById("taskName").value;
    const description = document.getElementById("taskDescription").value;
    const selectedDays = Array.from(
        document.querySelectorAll(".day-option input:checked")
    ).map(checkbox => checkbox.value);

    if (selectedDays.length === 0) {
        alert("Please select at least one day.");
        return;
    }

    await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description, days: selectedDays })
    });

    taskForm.reset();
    modal.classList.add("hidden");
    loadTasks();
});

function setTheme(dark) {
    document.body.classList.toggle("dark", dark);
    themeToggle.textContent = dark ? "☀️" : "🌙";
    themeToggle.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    themeToggle.setAttribute("title", dark ? "Switch to light mode" : "Switch to dark mode");
    themeToggle.setAttribute("aria-pressed", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
}

themeToggle.addEventListener("click", () => {
    setTheme(!document.body.classList.contains("dark"));
});

if (localStorage.getItem("theme") === "dark") setTheme(true);

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
}

updateDate();
loadTasks();
