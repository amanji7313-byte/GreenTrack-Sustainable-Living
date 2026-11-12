# GreenTrack – Sustainable Living Management System

GreenTrack is a beginner-friendly Python web project. It lets a user keep a daily record of electricity use, water use, waste generated, and one eco-friendly action.

## Features
- Create an account and log in
- Save daily sustainability records
- View monthly totals on a dashboard
- View and delete saved records
- Read simple eco-friendly suggestions
- Store information in an SQLite database

## Technology used
- Python
- Flask
- SQLite
- HTML
- CSS

## Requirements
- Python 3.9 or newer
- pip

## How to run on Windows

1. Extract the ZIP file.
2. Open the project folder in VS Code.
3. Open the terminal in that folder.
4. Create a virtual environment:

   `python -m venv venv`

5. Activate it in PowerShell:

   `.\venv\Scripts\Activate.ps1`

   If PowerShell blocks activation, you can use Command Prompt:

   `venv\\Scripts\\activate.bat`

6. Install Flask:

   `pip install -r requirements.txt`

7. Start the project:

   `python app.py`

8. Open this address in your browser:

   `http://127.0.0.1:5000`

9. Register a new account and start adding records.

## Project structure

- `app.py` – routes, login, database work and application logic
- `greentrack.db` – created automatically when the app runs
- `templates/` – HTML pages
- `static/style.css` – page styling
- `requirements.txt` – Python package list

## Important notes
- This is a learning/demo project, not a verified scientific carbon-footprint calculator.
- Usage totals are based only on the values entered by the user.
- Before deploying publicly, replace the development secret key, turn off Flask debug mode, add CSRF protection, and use HTTPS.
- Do not use a real or reused password while testing a student project.
