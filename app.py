
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)

import sqlite3
import os
import json
import uuid

from werkzeug.utils import secure_filename


# ---------------- FLASK CONFIGURATION ----------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY", "job_tracker_secret_key"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "database.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf"}


# ---------------- DATABASE CONNECTION ----------------

def get_db():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# ---------------- DATABASE INITIALIZATION ----------------

def init_db():

    conn = get_db()

    # Existing job applications table
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

    # AI resume analysis history table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resume_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_filename TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_description TEXT NOT NULL,
            match_score REAL NOT NULL,
            matched_skills TEXT,
            missing_skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------------- DASHBOARD ----------------

@app.route("/")
def index():

    search = request.args.get("search", "").strip()

    conn = get_db()

    jobs = conn.execute("""
        SELECT * FROM jobs
        WHERE company LIKE ? OR role LIKE ?
        ORDER BY id DESC
    """, (
        f"%{search}%",
        f"%{search}%"
    )).fetchall()

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


# ---------------- ADD JOB ----------------

@app.route("/add", methods=["GET", "POST"])
def add_job():

    if request.method == "POST":

        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        location = request.form.get("location", "").strip()
        applied_date = request.form.get("applied_date", "")
        status = request.form.get("status", "Applied")
        notes = request.form.get("notes", "").strip()

        valid_statuses = [
            "Applied", "Interview", "Selected", "Rejected"
        ]

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
        """, (
            company,
            role,
            location,
            applied_date,
            status,
            notes
        ))

        conn.commit()
        conn.close()

        flash(
            "Job application added successfully!",
            "success"
        )

        return redirect(url_for("index"))

    return render_template("add_job.html", job=None)


# ---------------- EDIT JOB ----------------

@app.route("/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    conn = get_db()

    job = conn.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,)
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

        valid_statuses = [
            "Applied", "Interview", "Selected", "Rejected"
        ]

        if not company or not role or not applied_date:

            conn.close()

            flash("Please fill all required fields.", "danger")

            return redirect(
                url_for("edit_job", job_id=job_id)
            )

        if status not in valid_statuses:

            conn.close()

            flash("Invalid application status.", "danger")

            return redirect(
                url_for("edit_job", job_id=job_id)
            )

        conn.execute("""
            UPDATE jobs
            SET company=?, role=?, location=?,
                applied_date=?, status=?, notes=?
            WHERE id=?
        """, (
            company,
            role,
            location,
            applied_date,
            status,
            notes,
            job_id
        ))

        conn.commit()
        conn.close()

        flash(
            "Job application updated successfully!",
            "success"
        )

        return redirect(url_for("index"))

    conn.close()

    return render_template("add_job.html", job=job)


# ---------------- DELETE JOB ----------------

@app.route("/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM jobs WHERE id = ?",
        (job_id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Job application deleted.",
        "success"
    )

    return redirect(url_for("index"))


# ---------------- AI RESUME ANALYZER ----------------

@app.route("/ai-match", methods=["GET", "POST"])
def ai_match():

    analysis = None

    if request.method == "POST":

        resume = request.files.get("resume")

        job_title = request.form.get(
            "job_title", ""
        ).strip()

        job_description = request.form.get(
            "job_description", ""
        ).strip()

        # Validate uploaded file
        if not resume or not resume.filename:

            flash(
                "Please upload your resume PDF.",
                "danger"
            )

            return redirect(url_for("ai_match"))

        if not job_title or not job_description:

            flash(
                "Please enter job title and description.",
                "danger"
            )

            return redirect(url_for("ai_match"))

        original_filename = secure_filename(resume.filename)

        if not original_filename.lower().endswith(".pdf"):

            flash(
                "Only PDF resumes are allowed.",
                "danger"
            )

            return redirect(url_for("ai_match"))

        # Validate actual PDF header
        header = resume.stream.read(5)
        resume.stream.seek(0)

        if header != b"%PDF-":

            flash(
                "Invalid PDF file. Please upload a valid PDF.",
                "danger"
            )

            return redirect(url_for("ai_match"))

        # Generate unique temporary filename
        temp_filename = uuid.uuid4().hex + ".pdf"

        temp_path = os.path.join(
            UPLOAD_FOLDER,
            temp_filename
        )

        try:

            # Save uploaded PDF temporarily
            resume.save(temp_path)

            # Import AI model only when required
            from models.resume_matcher import analyze_resume

            # Perform resume analysis
            result = analyze_resume(
                temp_path,
                job_description
            )

            # Save analysis in database
            conn = get_db()

            try:

                conn.execute("""
                    INSERT INTO resume_analyses
                    (
                        resume_filename,
                        job_title,
                        job_description,
                        match_score,
                        matched_skills,
                        missing_skills
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    original_filename,
                    job_title,
                    job_description,
                    result["match_score"],
                    json.dumps(result["matched_skills"]),
                    json.dumps(result["missing_skills"])
                ))

                conn.commit()

            finally:

                conn.close()

            # Prepare results for HTML template
            analysis = {
                "resume_filename": original_filename,
                "job_title": job_title,
                "match_score": result["match_score"],
                "resume_skills": result["resume_skills"],
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"]
            }

            flash(
                "Resume analyzed successfully!",
                "success"
            )

        except Exception as error:

            print("AI Analysis Error:", error)

            flash(
                "Resume analysis failed. Check that your PDF contains readable text and try again.",
                "danger"
            )

        finally:

            # Delete temporary uploaded PDF
            if os.path.exists(temp_path):

                os.remove(temp_path)

    # Fetch previous analysis history
    conn = get_db()

    history = conn.execute("""
        SELECT * FROM resume_analyses
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return render_template(
        "ai_match.html",
        analysis=analysis,
        history=history
    )


# ---------------- UPLOAD SIZE ERROR ----------------

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "Resume file is too large. Maximum size is 5 MB.",
        "danger"
    )

    return redirect(url_for("ai_match"))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)
