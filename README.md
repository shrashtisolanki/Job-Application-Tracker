# Job Application Tracker

A simple Python Full Stack web application that helps job seekers manage and track their job applications in one place.

## Features

- Add new job applications
- View all job applications
- Edit application details
- Delete applications
- Search by company name or job role
- Track application status
- Dashboard with application statistics

## Technology Stack

- **Frontend:** HTML, CSS, Bootstrap 5
- **Backend:** Python, Flask
- **Database:** SQLite
- **Template Engine:** Jinja2
- **Version Control:** Git and GitHub

## Project Structure

```text
JOB-APPLICATION-TRACKER/
│
├── app.py
├── database.db
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   └── add_job.html
│
└── static/
    └── style.css
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/shrashtisolanki/Job-Application-Tracker.git
```

### 2. Navigate to the project folder

```bash
cd Job-Application-Tracker
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install Flask

```bash
pip install flask
```

### 6. Run the application

```bash
python app.py
```

### 7. Open in your browser

http://127.0.0.1:5000

## Application Status

The application supports four statuses:

- Applied
- Interview
- Selected
- Rejected

## Database

SQLite is used to store job application details, including company name, job role, location, applied date, status and notes.

The database is automatically created when the application runs.

## Future Improvements

- User login and registration
- Application deadline reminders
- Data visualization and analytics
- Online deployment

## Author

**Shrashti Solanki**

GitHub: https://github.com/shrashtisolanki

---

Developed as a Python Full Stack Development project.
