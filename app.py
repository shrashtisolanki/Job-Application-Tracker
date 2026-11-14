
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "job_tracker_secret_key"

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            applied_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied',
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


# Dashboard
@app.route("/")
def index():
    search = request.args.get("search", "").strip()

    conn = get_db()

    jobs = conn.execute("""
        SELECT * FROM jobs
        WHERE company LIKE ? OR role LIKE ?
        ORDER BY id DESC
    """, (f"%{search}%", f"%{search}%")).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

    applied = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status='Applied'"
    ).fetchone()[0]

    interview = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status='Interview'"
    ).fetchone()[0]

    selected = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status='Selected'"
    ).fetchone()[0]

    rejected = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status='Rejected'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        jobs=jobs,
        total=total,
        applied=applied,
        interview=interview,
        selected=selected,
        rejected=rejected,
        search=search
    )


# Add new job
@app.route("/add", methods=["GET", "POST"])
def add_job():

    if request.method == "POST":

        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        location = request.form.get("location", "").strip()
        applied_date = request.form.get("applied_date", "")
        status = request.form.get("status", "Applied")
        notes = request.form.get("notes", "").strip()

        valid_statuses = ["Applied", "Interview", "Selected", "Rejected"]

        if not company or not role or not applied_date:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("add_job"))

        if status not in valid_statuses:
            flash("Invalid application status.", "danger")
            return redirect(url_for("add_job"))

        conn = get_db()

        conn.execute("""
            INSERT INTO jobs
            (company, role, location, applied_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company, role, location, applied_date, status, notes))

        conn.commit()
        conn.close()

        flash("Job application added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add_job.html", job=None)


# Edit job
@app.route("/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    conn = get_db()

    job = conn.execute(
        "SELECT * FROM jobs WHERE id = ?", (job_id,)
    ).fetchone()

    if job is None:
        conn.close()
        flash("Job application not found.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":

        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        location = request.form.get("location", "").strip()
        applied_date = request.form.get("applied_date", "")
        status = request.form.get("status", "Applied")
        notes = request.form.get("notes", "").strip()

        valid_statuses = ["Applied", "Interview", "Selected", "Rejected"]

        if not company or not role or not applied_date:
            conn.close()
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("edit_job", job_id=job_id))

        if status not in valid_statuses:
            conn.close()
            flash("Invalid application status.", "danger")
            return redirect(url_for("edit_job", job_id=job_id))

        conn.execute("""
            UPDATE jobs
            SET company=?, role=?, location=?,
                applied_date=?, status=?, notes=?
            WHERE id=?
        """, (
            company, role, location,
            applied_date, status, notes, job_id
        ))

        conn.commit()
        conn.close()

        flash("Job application updated successfully!", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template("add_job.html", job=job)


# Delete job
@app.route("/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM jobs WHERE id = ?", (job_id,)
    )

    conn.commit()
    conn.close()

    flash("Job application deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
