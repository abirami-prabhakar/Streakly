from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import date, timedelta

app = Flask(__name__)
DATABASE = "database.db"

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            monday INTEGER DEFAULT 0,
            tuesday INTEGER DEFAULT 0,
            wednesday INTEGER DEFAULT 0,
            thursday INTEGER DEFAULT 0,
            friday INTEGER DEFAULT 0,
            saturday INTEGER DEFAULT 0,
            sunday INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            completed_date TEXT NOT NULL,
            completed INTEGER DEFAULT 1,
            UNIQUE(task_id, completed_date),
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    today = date.today()
    day_name = today.strftime("%A").lower()
    today_string = today.isoformat()

    tasks = conn.execute(
        f"""SELECT * FROM tasks WHERE active = 1 AND {day_name} = 1 ORDER BY id DESC"""
    ).fetchall()

    result = []
    for task in tasks:
        completion = conn.execute(
            """SELECT completed FROM completions
               WHERE task_id = ? AND completed_date = ?""",
            (task["id"], today_string)
        ).fetchone()

        result.append({
            "id": task["id"],
            "name": task["name"],
            "description": task["description"],
            "completed": bool(completion["completed"]) if completion else False,
            "streak": calculate_streak(task["id"])
        })

    conn.close()
    return jsonify(result)

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    selected_days = data.get("days", [])

    if not name:
        return jsonify({"error": "Task name is required"}), 400

    values = [1 if day in selected_days else 0 for day in DAYS]

    conn = get_db()
    conn.execute("""
        INSERT INTO tasks (
            name, description, monday, tuesday, wednesday,
            thursday, friday, saturday, sunday
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [name, description] + values)
    conn.commit()
    conn.close()

    return jsonify({"message": "Task created successfully"}), 201

@app.route("/api/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    today = date.today().isoformat()
    conn = get_db()

    existing = conn.execute(
        """SELECT id, completed FROM completions
           WHERE task_id = ? AND completed_date = ?""",
        (task_id, today)
    ).fetchone()

    if existing:
        new_value = 0 if existing["completed"] else 1
        conn.execute(
            "UPDATE completions SET completed = ? WHERE id = ?",
            (new_value, existing["id"])
        )
    else:
        conn.execute(
            """INSERT INTO completions (task_id, completed_date, completed)
               VALUES (?, ?, 1)""",
            (task_id, today)
        )

    conn.commit()
    conn.close()
    return jsonify({"message": "Task updated"})

def calculate_streak(task_id):
    conn = get_db()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()

    if not task:
        conn.close()
        return 0

    streak = 0
    current_date = date.today()

    for _ in range(365):
        day_name = current_date.strftime("%A").lower()

        if task[day_name] == 1:
            completion = conn.execute(
                """SELECT completed FROM completions
                   WHERE task_id = ? AND completed_date = ?""",
                (task_id, current_date.isoformat())
            ).fetchone()

            if completion and completion["completed"]:
                streak += 1
            else:
                break

        current_date -= timedelta(days=1)

    conn.close()
    return streak

def calculate_overall_streak(conn, today):
    schedule_columns = [f"{day}" for day in DAYS]
    tasks = conn.execute(
        f"SELECT id, created_at, {', '.join(schedule_columns)} FROM tasks WHERE active = 1"
    ).fetchall()
    start_date = today - timedelta(days=364)
    completions = conn.execute(
        """SELECT task_id, completed_date FROM completions
           WHERE completed = 1 AND completed_date BETWEEN ? AND ?""",
        (start_date.isoformat(), today.isoformat())
    ).fetchall()
    completed_tasks = {
        (completion["task_id"], completion["completed_date"])
        for completion in completions
    }

    streak = 0
    current_date = today
    for _ in range(365):
        day_name = current_date.strftime("%A").lower()
        date_string = current_date.isoformat()
        scheduled_tasks = [
            task for task in tasks
            if task[day_name] == 1 and task["created_at"][:10] <= date_string
        ]
        if scheduled_tasks:
            if not all((task["id"], date_string) in completed_tasks for task in scheduled_tasks):
                break
            streak += 1
        current_date -= timedelta(days=1)

    return streak

@app.route("/api/stats")
def stats():
    conn = get_db()
    today = date.today()
    day_name = today.strftime("%A").lower()

    total = conn.execute(
        f"""SELECT COUNT(*) FROM tasks
            WHERE active = 1 AND {day_name} = 1"""
    ).fetchone()[0]

    completed = conn.execute(
        f"""SELECT COUNT(*) FROM tasks t
            JOIN completions c ON t.id = c.task_id
            WHERE t.active = 1
              AND t.{day_name} = 1
              AND c.completed_date = ?
              AND c.completed = 1""",
        (today.isoformat(),)
    ).fetchone()[0]

    percentage = round((completed / total) * 100) if total else 0

    week_start = today - timedelta(days=today.weekday())
    week = []
    for offset in range(7):
        current_date = week_start + timedelta(days=offset)
        current_day = current_date.strftime("%A").lower()
        scheduled = conn.execute(
            f"SELECT COUNT(*) FROM tasks t WHERE t.active = 1 AND t.{current_day} = 1 AND date(t.created_at) <= ?",
            (current_date.isoformat(),)
        ).fetchone()[0]
        done = conn.execute(
            f"""SELECT COUNT(*) FROM tasks t
                JOIN completions c ON t.id = c.task_id
                WHERE t.active = 1 AND t.{current_day} = 1
                  AND date(t.created_at) <= ?
                  AND c.completed_date = ? AND c.completed = 1""",
            (current_date.isoformat(), current_date.isoformat())
        ).fetchone()[0]
        week.append({
            "day": current_date.strftime("%a"),
            "date": current_date.isoformat(),
            "total": scheduled,
            "completed": done
        })

    overall_streak = calculate_overall_streak(conn, today)
    conn.close()

    return jsonify({
        "total": total,
        "completed": completed,
        "percentage": percentage,
        "streak": overall_streak,
        "today": today.isoformat(),
        "week": week
    })

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
