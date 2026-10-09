from urllib.parse import urlsplit
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth_bp
from app.models import db, User, StudentProfile, Department, Subject, Enrollment, Notification
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.utils import send_notification


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        login_id = form.login_id.data.strip()
        # Find user by username or email
        user = User.query.filter(
            (User.username == login_id) | (User.email == login_id.lower())
        ).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.username}!', 'success')

            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                if user.is_admin:
                    next_page = url_for('admin.dashboard')
                else:
                    next_page = url_for('student.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    form = RegistrationForm()
    # Populate departments dropdown
    departments = Department.query.order_by(Department.name).all()
    form.department_id.choices = [(d.id, f"{d.name} ({d.code})") for d in departments]

    if form.validate_on_submit():
        # Create user
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            role='student'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # get user.id

        # Create student profile
        profile = StudentProfile(
            user_id=user.id,
            student_id=form.student_id.data.strip().upper(),
            full_name=form.full_name.data.strip(),
            department_id=form.department_id.data,
            semester=form.semester.data,
            academic_year=form.academic_year.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None
        )
        db.session.add(profile)
        db.session.flush()

        # Auto-enroll student into subjects of their department and semester
        matching_subjects = Subject.query.filter_by(
            department_id=form.department_id.data,
            semester=form.semester.data
        ).all()
        for subj in matching_subjects:
            enrollment = Enrollment(
                student_id=profile.id,
                subject_id=subj.id,
                academic_year=form.academic_year.data.strip(),
                semester=form.semester.data
            )
            db.session.add(enrollment)

        # Welcome notification
        send_notification(
            user_id=user.id,
            title='Welcome to StudentHub!',
            message=f'Hello {profile.full_name}, your student account has been created successfully. Explore your dashboard and subjects.',
            link=url_for('student.dashboard')
        )

        db.session.commit()
        login_user(user)
        flash('Registration successful! Welcome to your student portal.', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been successfully updated.', 'success')
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.profile'))

    # If accessed via GET or form invalid, render profile or redirect
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('student.profile'))
