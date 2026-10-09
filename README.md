# 🎓 StudentHub — Smart Student Portal

**StudentHub** is a modern, responsive, full-stack Student Portal and Academic Management System designed for colleges and universities. Built with **Python (Flask)**, **SQLite / PostgreSQL**, and a sleek **Bootstrap 5 SaaS dashboard interface**, StudentHub delivers a complete pair of personalized experiences: an intuitive academic dashboard for students and a comprehensive administrative portal for faculty and administrators.

---

## 🌟 Key Features

### 👤 Student Portal
* **Personalized Dashboard**: Real-time academic metrics, student ID badges, department & semester tags, attendance progress ring, upcoming examinations, pending assignments countdown, and timetable preview.
* **Attendance Tracking**:
  * Automated calculation: $\text{Attendance \%} = \left(\frac{\text{Classes Attended}}{\text{Classes Conducted}}\right) \times 100$.
  * Subject-wise breakdown with progress bars.
  * **Automatic warning banner** and visual alerts for any subject falling below the **75% threshold**.
  * Filterable daily attendance history log.
  * Interactive Chart.js donut distribution.
* **Assignment Management**:
  * View course assignments, download teacher-provided prompt documents.
  * Upload submissions with file validation (PDF, DOCX, ZIP, source code) and submission notes.
  * Filter by *Pending*, *Submitted*, and *Graded*.
  * Review instructor marks and personalized feedback.
* **Examinations & Scorecards**:
  * Examination timetable with date, time, subject code, max marks, and exam room venue.
  * Verified grade scorecard with automated letter grade calculation ($A+, A, B+, B, C, D, F$).
  * Distinction/First Class classification and aggregate percentage tracker.
* **Interactive Weekly Timetable**:
  * Multi-day interactive tabbed grid (Monday – Saturday).
  * Automatically highlights current day's classes, classrooms, faculty, and recess periods.
* **Digital Learning Repository (Study Materials)**:
  * Filter and search study materials by keyword, subject, and material type (*Lecture Notes, PDF Documents, Previous Year Question Papers, Reference Books, Syllabus*).
  * Direct file download capability.
* **Campus Announcements & In-App Notifications**:
  * College-wide and department-specific notice feeds with categories (*Examination, Assignment, Event, Holiday, Academic*).
  * Pinned notices and priority badges (*Urgent, Important*).
  * Unread notification count badge and dropdown.
* **Profile & Security**:
  * Profile avatar upload, contact phone, residential address, and student bio.
  * Sensitive academic credentials (*Student ID, Department, Semester*) are locked to preserve data integrity.
  * Self-service password change system.

### 🛡️ Administrator Panel
* **Executive Dashboard**: System-wide statistics (student count, department distributions, campus attendance rate, pending assignments to grade).
* **Student Directory**: Search by name, email, or Student ID; filter by department and semester; view full student academic dossier; deactivate/activate accounts.
* **Department & Curriculum Management**: CRUD operations for academic departments, course codes, credit allocations, and faculty assignments.
* **Attendance Register**: Roster-based batch attendance marking (*Present, Absent, Excused*) with instant 'Mark All' toggles and session remarks.
* **Coursework Assignment Publishing**: Publish new assignments with deadlines, points, and reference file attachments; review submissions and enter grades.
* **Examination Timetable & Result Publication**: Schedule exam halls and publish verified marks with a single click.
* **Study Material Management**: Upload learning resources and question papers.
* **Notice Broadcast**: Publish college announcements that automatically generate in-app notifications for students.

### 🎨 Modern UI/UX
* **Dual Theme Engine**: Seamless Light & Dark modes persisted in `localStorage`.
* **Responsive Architecture**: Collapsible sidebar navigation (minimizes on desktop, off-canvas drawer on mobile).
* **Navy Blue / Slate SaaS Aesthetic**: Rounded cards (`border-radius: 0.85rem`), subtle shadows, clean typography (Inter font).
* **Chart.js Integration**: Interactive subject-wise bar charts and attendance donut breakdowns.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4 |
| **Backend** | Python 3.10+, Flask 3.1, Flask-Login, Flask-WTF, WTForms, Werkzeug |
| **Database** | SQLite (Default for development) / PostgreSQL ready via SQLAlchemy ORM |
| **Security** | PBKDF2:SHA256 password hashing, CSRF token validation, role-based decorators (`@admin_required`, `@student_required`), secure file uploads |
| **Deployment** | Waitress (Windows WSGI) / Gunicorn (Linux/macOS WSGI) |

---

## 📁 Project Directory Structure

```text
studenthub/
├── app/
│   ├── __init__.py           # Application factory (create_app), extension initialization, filters
│   ├── models.py             # SQLAlchemy schemas (User, StudentProfile, Department, Subject, etc.)
│   ├── forms.py              # Flask-WTF forms with CSRF and validation rules
│   ├── utils.py              # Role decorators, secure file handling, grade calculation helpers
│   ├── auth/                 # Authentication blueprint (login, register, logout, password)
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── student/              # Student portal blueprint (dashboard, attendance, assignments, etc.)
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── admin/                # Administrator blueprint (roster, grading, timetable, notices)
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html         # Master dashboard template (sidebar, topbar, theme toggle)
│   │   ├── auth_base.html    # Centered authentication layout
│   │   ├── auth/             # Login & Register views
│   │   ├── student/          # Student portal views
│   │   ├── admin/            # Administrator views
│   │   └── errors/           # 403, 404, 500 custom error pages
│   └── static/
│       ├── css/style.css     # Master SaaS styles, color variables, dark mode tokens
│       ├── js/main.js        # Sidebar toggles, theme switcher, search filters
│       └── uploads/          # Managed directory for avatars, materials, and submissions
├── tests/
│   ├── conftest.py           # In-memory test client and database fixture
│   ├── test_auth.py          # Authentication and RBAC tests
│   └── test_routes.py        # Student and Admin route accessibility tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore patterns
├── config.py                 # Configuration profiles (Development, Testing, Production)
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
├── seed.py                   # Pre-populates database with demo academic data
└── README.md                 # Complete documentation
```

---

## ⚡ Quick Start Installation Guide

### Prerequisites
* **Python 3.10** or higher installed ([Download Python](https://www.python.org/downloads/))
* **Git** installed ([Download Git](https://git-scm.com/))
* **Visual Studio Code** (or your favorite code editor)

---

### Step 1: Open the Project in VS Code
Open your terminal or command prompt:
```bash
cd "C:\Users\user\.gemini\antigravity\scratch\studenthub"
code .
```

---

### Step 2: Create & Activate Python Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an Execution Policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On macOS / Linux:
cp .env.example .env
```

---

### Step 5: Initialize & Seed the Database
Run the pre-configured seed script to build the database schema and populate realistic demo data:
```bash
python seed.py
```

---

### Step 6: Start the Development Server
```bash
python run.py
```
Open your web browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Credentials

The seed script initializes two pre-configured accounts:

### 🎓 Student Account
* **Username**: `student1` *(or email: `alex.morgan@campus.edu`)*
* **Password**: `password123`
* **Profile**: Alex Morgan (Junior, Computer Science & Engineering, Semester 5)
* **Highlights**: Enrolled in 5 courses, realistic attendance data (including one course below 75% for warning testing), graded assignments, and scheduled mid-term exams.

### 🛡️ Administrator Account
* **Username**: `admin` *(or email: `admin@studenthub.edu`)*
* **Password**: `admin123`
* **Role**: System Administrator / Faculty Lead
* **Highlights**: Full access to student roster, attendance register, grading modals, exam scheduler, timetable designer, and campus notices.

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
pytest -v
```

This verifies:
1. Password hashing integrity (Werkzeug secure PBKDF2)
2. Student and admin login workflows
3. Role-based access control (ensuring students cannot access `/admin/*` routes)
4. Unauthenticated route redirection
5. Full accessibility of student and admin dashboard views

---

## 🚀 Production Deployment Guide

### 1. Running with a Production WSGI Server

Never use Flask's built-in development server in a production environment.

**On Windows (using Waitress):**
```powershell
waitress-serve --listen=0.0.0.0:5000 run:app
```

**On Linux / macOS (using Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

---

### 2. Migrating to PostgreSQL

StudentHub is structured with SQLAlchemy ORM, making migrating from SQLite to PostgreSQL straightforward:

1. Install the PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```
2. In your `.env` file or cloud environment settings, update `DATABASE_URL`:
   ```env
   DATABASE_URL=postgresql://username:password@db-host:5432/studenthub_db
   ```
3. Run `python seed.py` or initialize tables in Python:
   ```python
   from app import create_app, db
   app = create_app('production')
   with app.app_context():
       db.create_all()
   ```

---

### 3. Deploying to Render / Railway / Heroku

1. Create a `Procfile` (for Heroku / Render):
   ```text
   web: gunicorn run:app
   ```
2. Set Environment Variables in your hosting dashboard:
   * `FLASK_ENV=production`
   * `SECRET_KEY=<generate-a-strong-random-key>`
   * `DATABASE_URL=<your-hosted-postgresql-connection-string>`
3. Push your repository to GitHub and connect to your hosting provider.

---

## 📦 Pushing to GitHub

To push your project to a GitHub repository:

```bash
git init
git add .
git commit -m "feat: complete StudentHub smart portal with student & admin dashboards"
git branch -M main
git remote add origin https://github.com/<your-username>/studenthub.git
git push -u origin main
```

---

## 🔒 Security Best Practices Implemented
* **Zero Plaintext Passwords**: Password hashing via salted PBKDF2-SHA256 algorithms.
* **Strict CSRF Defense**: Every POST, PUT, and DELETE action is protected with CSRF tokens.
* **Role-Based Authorization**: Route-level decorators check `current_user.is_admin` and `current_user.is_student`.
* **Safe File Management**: Uses `secure_filename()`, unique UUID prefixes, file type extensions whitelisting, and a 16MB file size ceiling.
* **SQL Injection Immunity**: All database queries utilize SQLAlchemy's parameterized ORM abstraction.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
