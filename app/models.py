from datetime import datetime, date, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account model for authentication and role authorization."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    @property
    def is_student(self) -> bool:
        return self.role == 'student'

    def __repr__(self) -> str:
        return f'<User {self.username} [{self.role}]>'


class Department(db.Model):
    """Department / Branch model."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)  # e.g., 'CSE', 'IT', 'ECE'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    students = db.relationship('StudentProfile', backref='department', lazy='dynamic')
    subjects = db.relationship('Subject', backref='department', lazy='dynamic')
    timetable_entries = db.relationship('TimetableEntry', backref='department', lazy='dynamic')
    announcements = db.relationship('Announcement', backref='department', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Department {self.code}: {self.name}>'


class StudentProfile(db.Model):
    """Profile details for registered students."""
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)  # e.g. STU2026001
    full_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False, default=1)
    academic_year = db.Column(db.String(20), nullable=False, default='2025-2026')
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    avatar = db.Column(db.String(200), default='default-avatar.svg')
    bio = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    submissions = db.relationship('AssignmentSubmission', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('Result', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<StudentProfile {self.student_id} - {self.full_name}>'


class Subject(db.Model):
    """Curriculum courses/subjects."""
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # e.g. CS501
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, default=3, nullable=False)
    faculty_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='subject', lazy='dynamic')
    attendance_records = db.relationship('AttendanceRecord', backref='subject', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='subject', lazy='dynamic')
    examinations = db.relationship('Examination', backref='subject', lazy='dynamic')
    timetable_entries = db.relationship('TimetableEntry', backref='subject', lazy='dynamic')
    study_materials = db.relationship('StudyMaterial', backref='subject', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Subject {self.code} - {self.name}>'


class Enrollment(db.Model):
    """Mapping student to enrolled subjects."""
    __tablename__ = 'enrollments'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'academic_year', name='uq_student_subject_year'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False, default='2025-2026')
    semester = db.Column(db.Integer, nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class AttendanceRecord(db.Model):
    """Daily attendance records per subject per student."""
    __tablename__ = 'attendance_records'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'date', name='uq_student_subject_date'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False, default='Present')  # Present, Absent, Excused
    remarks = db.Column(db.String(200), nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    recorder = db.relationship('User', foreign_keys=[recorded_by])


class Assignment(db.Model):
    """Course assignments posted by admin/faculty."""
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_attachment = db.Column(db.String(255), nullable=True)
    assigned_date = db.Column(db.Date, default=date.today, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    max_marks = db.Column(db.Float, default=100.0, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    creator = db.relationship('User', foreign_keys=[created_by])
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')


class AssignmentSubmission(db.Model):
    """Submissions uploaded by students for assignments."""
    __tablename__ = 'assignment_submissions'
    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='uq_assignment_student'),
    )

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    submission_text = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='Submitted', nullable=False)  # Submitted, Graded, Late
    marks_obtained = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    graded_at = db.Column(db.DateTime, nullable=True)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    grader = db.relationship('User', foreign_keys=[graded_by])


class Examination(db.Model):
    """Examination schedule."""
    __tablename__ = 'examinations'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_name = db.Column(db.String(100), nullable=False)  # e.g., 'Mid-Term 2026', 'Final Exam'
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    max_marks = db.Column(db.Float, default=100.0, nullable=False)
    passing_marks = db.Column(db.Float, default=40.0, nullable=False)
    academic_year = db.Column(db.String(20), nullable=False, default='2025-2026')
    semester = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    results = db.relationship('Result', backref='examination', lazy='dynamic', cascade='all, delete-orphan')


class Result(db.Model):
    """Exam scores and grades achieved by students."""
    __tablename__ = 'results'
    __table_args__ = (
        db.UniqueConstraint('examination_id', 'student_id', name='uq_examination_student'),
    )

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5), nullable=False)  # A+, A, B+, B, C, D, F
    remarks = db.Column(db.String(200), nullable=True)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class TimetableEntry(db.Model):
    """Weekly class timetable entries."""
    __tablename__ = 'timetable_entries'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.String(15), nullable=False)  # Monday, Tuesday, ...
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    is_break = db.Column(db.Boolean, default=False, nullable=False)
    break_title = db.Column(db.String(50), nullable=True)  # e.g., 'Lunch Break'
    classroom = db.Column(db.String(50), nullable=True)
    faculty_name = db.Column(db.String(100), nullable=True)


class StudyMaterial(db.Model):
    """Course study materials and downloads."""
    __tablename__ = 'study_materials'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    material_type = db.Column(db.String(50), nullable=False)  # 'Lecture Notes', 'PDF Document', 'Previous Question Paper', 'Reference Book', 'Syllabus'
    file_path = db.Column(db.String(255), nullable=False)
    file_size_kb = db.Column(db.Integer, default=0, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    uploader = db.relationship('User', foreign_keys=[uploaded_by])


class Announcement(db.Model):
    """Announcements and campus notices."""
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Academic', nullable=False)  # Academic, Examination, Assignment, Holiday, Event, Department, General
    priority = db.Column(db.String(20), default='Normal', nullable=False)  # Normal, Important, Urgent
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)  # None = College-wide
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    creator = db.relationship('User', foreign_keys=[created_by])


class Notification(db.Model):
    """In-app notifications for individual users."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(200), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
