# University Management System

A Flask and SQLite university management application with student, parent, faculty, and admin dashboards.

## Requirements

- Python 3.10 or newer
- Flask
- python-dotenv

## Setup on Windows

Open PowerShell in the project folder:

```powershell
cd "project folder path"
```

Create or activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Environment Configuration

The application reads secrets from `.env` in the project root.

Create `.env` from the example file:

```powershell
Copy-Item .env.example .env
```

The file should contain:

```env
FLASK_SECRET_KEY=change-this-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=passwords
```

`.env` is intentionally excluded by `.gitignore` because it contains private configuration. Keep `.env.example` available for other developers.

## Database

The application creates the required SQLite tables and default programs, branches, subjects, and events automatically when `app.py` starts.

To run the standalone database initializer:

```powershell
.\.venv\Scripts\python.exe initialize_db.py
```

The local database file is `elite.db`.

## Run the Application

```powershell
.\.venv\Scripts\python.exe app.py
```

Open the application at:

```text
http://127.0.0.1:5000
```

## Main Accounts

Admin login uses the values in `.env`

Students, parents, and faculty use the signup pages to create accounts. Faculty registration includes program, branch, teaching year, and one subject.

## Main Features

- Student signup with automatically assigned three-digit student IDs
- Student dashboard with profile, subjects, events, and faculty announcements
- Parent signup and dashboard access linked to a student
- Faculty signup with program, branch, teaching year, and subject assignment
- Faculty notifications sent to all students or a selected year
- Faculty sent-announcement history
- Admin management of students and faculty
- Admin notification activity and contact details
- Contact form submissions visible in the admin dashboard
