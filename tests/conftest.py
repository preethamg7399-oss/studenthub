import pytest
from app import create_app
from app.models import db, User, StudentProfile, Department, Subject, Enrollment


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()

        # Create demo department
        dept = Department(code='CSE', name='Computer Science', description='CSE Dept')
        db.session.add(dept)
        db.session.flush()

        # Create subjects
        subj = Subject(code='CS101', name='Intro to Programming', department_id=dept.id, semester=1, credits=3, faculty_name='Dr. Smith')
        db.session.add(subj)
        db.session.flush()

        # Create admin user
        admin = User(username='admin', email='admin@campus.edu', role='admin', is_active=True)
        admin.set_password('admin123')
        db.session.add(admin)

        # Create student user & profile
        student = User(username='student1', email='student1@campus.edu', role='student', is_active=True)
        student.set_password('password123')
        db.session.add(student)
        db.session.flush()

        profile = StudentProfile(
            user_id=student.id,
            student_id='STU2026001',
            full_name='Test Student',
            department_id=dept.id,
            semester=1,
            academic_year='2025-2026'
        )
        db.session.add(profile)
        db.session.flush()

        enrollment = Enrollment(
            student_id=profile.id,
            subject_id=subj.id,
            academic_year='2025-2026',
            semester=1
        )
        db.session.add(enrollment)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
