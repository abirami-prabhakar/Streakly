# Streakly

A simple productivity tracker based on days of the week.

## Features

- Create recurring tasks
- Select specific days of the week
- Mark today's tasks complete
- Track scheduled-day streaks
- View daily progress

## Run locally

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app.py
```

Open:

http://127.0.0.1:5000

## Run tests

```bash
pytest
```

## Run with Docker

```bash
docker build -t streakly .
docker run -p 5000:5000 streakly
```
