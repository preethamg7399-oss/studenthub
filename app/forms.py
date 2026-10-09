from datetime import date
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, SelectField, IntegerField, FloatField,
    DateField, TimeField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length,
    ValidationError, Optional, NumberRange
)
from app.models import User, StudentProfile


class LoginForm(FlaskForm):
    """User login form."""
    login_id = StringField('Username or Email', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Student self-registration form."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    student_id = StringField('Student ID / Roll No.', validators=[DataRequired(), Length(min=4, max=20)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    semester = SelectField('Semester', coerce=int, choices=[(i, f"Semester {i}") for i in range(1, 9)], validators=[DataRequired()])
    academic_year = StringField('Academic Year', default='2025-2026', validators=[DataRequired(), Length(max=20)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.strip()).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('This email address is already registered.')

    def validate_student_id(self, student_id):
        profile = StudentProfile.query.filter_by(student_id=student_id.data.strip()).first()
        if profile:
            raise ValidationError('This Student ID is already registered in the system.')


class ChangePasswordForm(FlaskForm):
    """Change user password form."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='New passwords must match.')
    ])
    submit = SubmitField('Update Password')


class StudentProfileUpdateForm(FlaskForm):
    """Student profile editable fields form."""
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Residential Address', validators=[Optional(), Length(max=200)])
    bio = TextAreaField('About Me / Bio', validators=[Optional(), Length(max=500)])
    avatar = FileField('Profile Picture', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (JPG, PNG, WEBP)!')
    ])
    submit = SubmitField('Save Profile Changes')


class DepartmentForm(FlaskForm):
    """Admin department form."""
    code = StringField('Department Code (e.g. CSE)', validators=[DataRequired(), Length(min=2, max=10)])
    name = StringField('Department Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Department')


class SubjectForm(FlaskForm):
    """Admin subject / course form."""
    code = StringField('Subject Code (e.g. CS501)', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Subject Name', validators=[DataRequired(), Length(min=3, max=100)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    semester = SelectField('Semester', coerce=int, choices=[(i, f"Semester {i}") for i in range(1, 9)], validators=[DataRequired()])
    credits = IntegerField('Credits', default=3, validators=[DataRequired(), NumberRange(min=1, max=10)])
    faculty_name = StringField('Faculty In-Charge', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Save Subject')


class AssignmentForm(FlaskForm):
    """Admin assignment creation/edit form."""
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    title = StringField('Assignment Title', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description / Requirements', validators=[DataRequired()])
    due_date = StringField('Due Date & Time (YYYY-MM-DDTHH:MM)', validators=[DataRequired()])
    max_marks = FloatField('Maximum Marks', default=100.0, validators=[DataRequired(), NumberRange(min=1)])
    attachment = FileField('Attach File (Optional)', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'zip', 'txt', 'py', 'java'], 'Documents, Zip, Code files only!')
    ])
    submit = SubmitField('Publish Assignment')


class AssignmentSubmissionForm(FlaskForm):
    """Student assignment submission form."""
    submission_text = TextAreaField('Submission Notes / Answer Text', validators=[Optional()])
    submission_file = FileField('Upload Assignment File (PDF, DOCX, ZIP, Code)', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'zip', 'txt', 'py', 'java', 'cpp', 'html'], 'Allowed formats: PDF, DOC, ZIP, Code files')
    ])
    submit = SubmitField('Submit Assignment')


class GradeSubmissionForm(FlaskForm):
    """Admin grade submission form."""
    marks_obtained = FloatField('Marks Obtained', validators=[DataRequired(), NumberRange(min=0)])
    feedback = TextAreaField('Instructor Feedback', validators=[Optional()])
    submit = SubmitField('Save Grade')


class ExaminationForm(FlaskForm):
    """Admin examination creation form."""
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    exam_name = StringField('Exam Name (e.g. Mid-Term, End-Semester)', validators=[DataRequired(), Length(max=100)])
    exam_date = DateField('Exam Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    venue = StringField('Venue / Classroom', validators=[DataRequired(), Length(max=100)])
    max_marks = FloatField('Max Marks', default=100.0, validators=[DataRequired()])
    passing_marks = FloatField('Passing Marks', default=40.0, validators=[DataRequired()])
    academic_year = StringField('Academic Year', default='2025-2026', validators=[DataRequired()])
    semester = SelectField('Semester', coerce=int, choices=[(i, f"Semester {i}") for i in range(1, 9)], validators=[DataRequired()])
    is_published = BooleanField('Publish Schedule to Students', default=True)
    submit = SubmitField('Save Examination')


class ResultForm(FlaskForm):
    """Admin result entry form."""
    examination_id = SelectField('Examination', coerce=int, validators=[DataRequired()])
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    marks_obtained = FloatField('Marks Obtained', validators=[DataRequired(), NumberRange(min=0)])
    remarks = StringField('Remarks', validators=[Optional(), Length(max=200)])
    is_published = BooleanField('Publish Result', default=True)
    submit = SubmitField('Save Result')


class TimetableEntryForm(FlaskForm):
    """Admin timetable entry form."""
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    semester = SelectField('Semester', coerce=int, choices=[(i, f"Semester {i}") for i in range(1, 9)], validators=[DataRequired()])
    day_of_week = SelectField('Day of Week', choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')
    ], validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    is_break = BooleanField('Is Break Period?')
    break_title = StringField('Break Title (e.g., Lunch Break)', validators=[Optional(), Length(max=50)])
    subject_id = SelectField('Subject', coerce=int, validators=[Optional()])
    classroom = StringField('Classroom / Lab', validators=[Optional(), Length(max=50)])
    faculty_name = StringField('Faculty Name', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save Timetable Entry')


class StudyMaterialForm(FlaskForm):
    """Admin study material upload form."""
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    title = StringField('Material Title', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', validators=[Optional()])
    material_type = SelectField('Type', choices=[
        ('Lecture Notes', 'Lecture Notes'),
        ('PDF Document', 'PDF Document'),
        ('Previous Question Paper', 'Previous Question Paper'),
        ('Reference Book', 'Reference Book'),
        ('Syllabus', 'Syllabus')
    ], validators=[DataRequired()])
    file = FileField('Upload Document (PDF, DOCX, PPTX, TXT, ZIP)', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'zip'], 'Allowed formats: PDF, DOC, PPT, ZIP, TXT')
    ])
    submit = SubmitField('Upload Study Material')


class AnnouncementForm(FlaskForm):
    """Admin announcement creation form."""
    title = StringField('Title', validators=[DataRequired(), Length(max=150)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Academic', 'Academic'),
        ('Examination', 'Examination'),
        ('Assignment', 'Assignment'),
        ('Holiday', 'Holiday'),
        ('Event', 'Event'),
        ('Department', 'Department'),
        ('General', 'General')
    ], default='Academic', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('Normal', 'Normal'),
        ('Important', 'Important'),
        ('Urgent', 'Urgent')
    ], default='Normal', validators=[DataRequired()])
    department_id = SelectField('Target Department (Optional - All if None)', coerce=int, validators=[Optional()])
    is_pinned = BooleanField('Pin to Top of Notices')
    submit = SubmitField('Publish Announcement')
