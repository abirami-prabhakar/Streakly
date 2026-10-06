import os
import tempfile
import pytest
from datetime import date

import app as application
from app import app, init_db

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config["TESTING"] = True
    original_database = application.DATABASE
    application.DATABASE = db_path
    init_db()

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)
    application.DATABASE = original_database

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200

def test_create_task(client):
    response = client.post(
        "/api/tasks",
        json={
            "name": "DSA Practice",
            "description": "Solve two problems",
            "days": ["monday", "wednesday", "friday"]
        }
    )
    assert response.status_code == 201

def test_empty_tasks(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json == []

def test_stats_include_database_backed_week_and_streak(client):
    response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.json["total"] == 0
    assert response.json["completed"] == 0
    assert response.json["percentage"] == 0
    assert response.json["streak"] == 0
    assert len(response.json["week"]) == 7
    assert all(day["total"] == 0 and day["completed"] == 0 for day in response.json["week"])

def test_stats_reflect_completed_task(client):
    today = date.today()
    day_name = today.strftime("%A").lower()
    created = client.post(
        "/api/tasks",
        json={"name": "Read", "days": [day_name]}
    )
    assert created.status_code == 201

    tasks = client.get("/api/tasks").json
    assert len(tasks) == 1
    assert client.post(f"/api/tasks/{tasks[0]['id']}/complete").status_code == 200

    stats = client.get("/api/stats").json
    today_stats = stats["week"][today.weekday()]
    assert stats["total"] == 1
    assert stats["completed"] == 1
    assert stats["percentage"] == 100
    assert stats["streak"] == 1
    assert today_stats["total"] == 1
    assert today_stats["completed"] == 1
