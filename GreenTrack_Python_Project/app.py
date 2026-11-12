from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"
DATABASE = "greentrack.db"


# Open a connection to the SQLite database.
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create the tables when the project is started for the first time.
def create_tables():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            record_date TEXT NOT NULL,
            electricity REAL NOT NULL,
            water REAL NOT NULL,
            waste REAL NOT NULL,
            eco_action TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    connection.commit()
    connection.close()


# Pages below this decorator can only be opened after login.
def login_required(page_function):
    @wraps(page_function)
    def check_login(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return page_function(*args, **kwargs)
    return check_login


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all the fields.")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must contain at least 6 characters.")
            return render_template("register.html")

        connection = get_db_connection()
        try:
            hashed_password = generate_password_hash(password)
            connection.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            connection.commit()
            flash("Account created. You can now log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("This email is already registered.")
        finally:
            connection.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_db_connection()
        user = connection.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        connection.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))

        flash("Incorrect email or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    connection = get_db_connection()
    records = connection.execute(
        """SELECT * FROM records
           WHERE user_id = ?
           ORDER BY record_date DESC, id DESC
           LIMIT 5""",
        (session["user_id"],)
    ).fetchall()

    month = date.today().strftime("%Y-%m")
    totals = connection.execute(
        """SELECT
             COALESCE(SUM(electricity), 0) AS electricity,
             COALESCE(SUM(water), 0) AS water,
             COALESCE(SUM(waste), 0) AS waste,
             COUNT(*) AS days
           FROM records
           WHERE user_id = ? AND substr(record_date, 1, 7) = ?""",
        (session["user_id"], month)
    ).fetchone()
    connection.close()

    return render_template("dashboard.html", records=records, totals=totals)


@app.route("/add-record", methods=["GET", "POST"])
@login_required
def add_record():
    if request.method == "POST":
        record_date = request.form.get("record_date", "")
        eco_action = request.form.get("eco_action", "").strip()

        try:
            electricity = float(request.form.get("electricity", ""))
            water = float(request.form.get("water", ""))
            waste = float(request.form.get("waste", ""))

            if electricity < 0 or water < 0 or waste < 0:
                raise ValueError

            date.fromisoformat(record_date)
        except (ValueError, TypeError):
            flash("Enter a valid date and non-negative numbers.")
            return render_template("add_record.html", today=date.today().isoformat())

        connection = get_db_connection()
        connection.execute(
            """INSERT INTO records
               (user_id, record_date, electricity, water, waste, eco_action)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session["user_id"], record_date, electricity, water, waste, eco_action)
        )
        connection.commit()
        connection.close()

        flash("Your daily record has been saved.")
        return redirect(url_for("dashboard"))

    return render_template("add_record.html", today=date.today().isoformat())


@app.route("/history")
@login_required
def history():
    connection = get_db_connection()
    records = connection.execute(
        """SELECT * FROM records
           WHERE user_id = ?
           ORDER BY record_date DESC, id DESC""",
        (session["user_id"],)
    ).fetchall()
    connection.close()
    return render_template("history.html", records=records)


@app.route("/delete-record/<int:record_id>", methods=["POST"])
@login_required
def delete_record(record_id):
    connection = get_db_connection()
    connection.execute(
        "DELETE FROM records WHERE id = ? AND user_id = ?",
        (record_id, session["user_id"])
    )
    connection.commit()
    connection.close()
    flash("Record deleted.")
    return redirect(url_for("history"))


@app.route("/tips")
@login_required
def tips():
    suggestions = [
        "Switch off lights, fans and chargers when they are not in use.",
        "Use a reusable water bottle instead of single-use plastic bottles.",
        "Repair leaking taps to avoid wasting clean water.",
        "Separate wet and dry waste before disposal.",
        "Walk, cycle or use public transport for short journeys when possible.",
        "Carry a reusable bag while shopping."
    ]
    return render_template("tips.html", suggestions=suggestions)


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
