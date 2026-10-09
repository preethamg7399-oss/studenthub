from datetime import datetime, date
from pathlib import Path
from flask import render_template, redirect, url_for, flash, request, current_app, send_from_directory, abort
from flask_login import current_user, login_required
from app.student import student_bp
from app.models import (
    db, StudentProfile, Department, Subject, Enrollment,
    AttendanceRecord, Assignment, AssignmentSubmission,
    Examination, Result, TimetableEntry, StudyMaterial,
    Announcement, Notification
)
from app.forms import StudentProfileUpdateForm, AssignmentSubmissionForm, ChangePasswordForm
from app.utils import student_required, save_uploaded_file


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    profile = current_user.student_profile
    if not profile:
        flash('Student profile not found. Please contact administration.', 'danger')
        return redirect(url_for('auth.logout'))

    # Get enrolled subjects
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()
    subject_ids = [e.subject_id for e in enrollments]
    total_subjects = len(subject_ids)

    # Attendance statistics
    attendance_records = AttendanceRecord.query.filter_by(student_id=profile.id).all()
    total_classes = len(attendance_records)
    attended_classes = sum(1 for a in attendance_records if a.status == 'Present')
    overall_attendance = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 100.0

    # Upcoming examinations
    today = date.today()
    upcoming_exams = Examination.query.filter(
        Examination.subject_id.in_(subject_ids) if subject_ids else False,
        Examination.exam_date >= today,
        Examination.is_published == True
    ).order_by(Examination.exam_date.asc(), Examination.start_time.asc()).limit(5).all()

    # Pending assignments
    all_assignments = Assignment.query.filter(
        Assignment.subject_id.in_(subject_ids) if subject_ids else False
    ).order_by(Assignment.due_date.asc()).all()
    
    submitted_assignment_ids = {
        s.assignment_id for s in AssignmentSubmission.query.filter_by(student_id=profile.id).all()
    }
    pending_assignments = [a for a in all_assignments if a.id not in submitted_assignment_ids]
    pending_count = len(pending_assignments)

    # Recent announcements (department-specific or campus-wide)
    recent_announcements = Announcement.query.filter(
        (Announcement.department_id == profile.department_id) | (Announcement.department_id.is_(None))
    ).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(5).all()

    # Upcoming events (category = 'Event')
    upcoming_events = Announcement.query.filter(
        ((Announcement.department_id == profile.department_id) | (Announcement.department_id.is_(None))),
        Announcement.category == 'Event'
    ).order_by(Announcement.created_at.desc()).limit(3).all()

    # Timetable preview for today
    day_name = datetime.now().strftime('%A')
    today_timetable = TimetableEntry.query.filter_by(
        department_id=profile.department_id,
        semester=profile.semester,
        day_of_week=day_name
    ).order_by(TimetableEntry.start_time.asc()).all()

    # Subject-wise attendance summary for Chart.js
    subject_attendance_data = []
    for subj_id in subject_ids:
        subj = db.session.get(Subject, subj_id)
        if not subj:
            continue
        subj_records = [r for r in attendance_records if r.subject_id == subj_id]
        conducted = len(subj_records)
        present = sum(1 for r in subj_records if r.status == 'Present')
        pct = round((present / conducted * 100), 1) if conducted > 0 else 100.0
        subject_attendance_data.append({
            'code': subj.code,
            'name': subj.name,
            'conducted': conducted,
            'present': present,
            'percentage': pct
        })

    return render_template(
        'student/dashboard.html',
        profile=profile,
        total_subjects=total_subjects,
        overall_attendance=overall_attendance,
        upcoming_exams=upcoming_exams,
        pending_count=pending_count,
        pending_assignments=pending_assignments[:4],
        recent_announcements=recent_announcements,
        upcoming_events=upcoming_events,
        today_timetable=today_timetable,
        today_name=day_name,
        subject_attendance_data=subject_attendance_data
    )


@student_bp.route('/attendance')
@login_required
@student_required
def attendance():
    profile = current_user.student_profile
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()
    subject_ids = [e.subject_id for e in enrollments]

    all_records = AttendanceRecord.query.filter_by(student_id=profile.id)\
        .order_by(AttendanceRecord.date.desc(), AttendanceRecord.created_at.desc()).all()

    total_classes = len(all_records)
    attended_classes = sum(1 for r in all_records if r.status == 'Present')
    missed_classes = sum(1 for r in all_records if r.status == 'Absent')
    excused_classes = sum(1 for r in all_records if r.status == 'Excused')
    overall_percentage = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 100.0

    # Subject breakdown
    subject_stats = []
    low_attendance_count = 0
    for subj_id in subject_ids:
        subj = db.session.get(Subject, subj_id)
        if not subj:
            continue
        subj_records = [r for r in all_records if r.subject_id == subj_id]
        conducted = len(subj_records)
        present = sum(1 for r in subj_records if r.status == 'Present')
        absent = sum(1 for r in subj_records if r.status == 'Absent')
        excused = sum(1 for r in subj_records if r.status == 'Excused')
        pct = round((present / conducted * 100), 1) if conducted > 0 else 100.0
        if pct < 75.0 and conducted > 0:
            low_attendance_count += 1
        subject_stats.append({
            'subject': subj,
            'conducted': conducted,
            'present': present,
            'absent': absent,
            'excused': excused,
            'percentage': pct,
            'is_low': pct < 75.0 and conducted > 0
        })

    # Subject filter for history table
    selected_subject_id = request.args.get('subject_id', type=int)
    if selected_subject_id:
        history_records = [r for r in all_records if r.subject_id == selected_subject_id]
    else:
        history_records = all_records

    return render_template(
        'student/attendance.html',
        profile=profile,
        total_classes=total_classes,
        attended_classes=attended_classes,
        missed_classes=missed_classes,
        excused_classes=excused_classes,
        overall_percentage=overall_percentage,
        subject_stats=subject_stats,
        low_attendance_count=low_attendance_count,
        history_records=history_records,
        subjects=[db.session.get(Subject, sid) for sid in subject_ids if db.session.get(Subject, sid)],
        selected_subject_id=selected_subject_id
    )


@student_bp.route('/assignments')
@login_required
@student_required
def assignments():
    profile = current_user.student_profile
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()
    subject_ids = [e.subject_id for e in enrollments]

    all_assignments = Assignment.query.filter(
        Assignment.subject_id.in_(subject_ids) if subject_ids else False
    ).order_by(Assignment.due_date.asc()).all()

    # Student submissions mapped by assignment_id
    submissions = {
        s.assignment_id: s for s in AssignmentSubmission.query.filter_by(student_id=profile.id).all()
    }

    # Filter tab: all, pending, submitted, graded
    status_filter = request.args.get('filter', 'all')
    assignment_items = []
    now = datetime.utcnow()

    for assign in all_assignments:
        sub = submissions.get(assign.id)
        if sub:
            status = 'Graded' if sub.marks_obtained is not None else 'Submitted'
        else:
            status = 'Overdue' if assign.due_date < now else 'Pending'

        if status_filter == 'pending' and status not in ('Pending', 'Overdue'):
            continue
        if status_filter == 'submitted' and status != 'Submitted':
            continue
        if status_filter == 'graded' and status != 'Graded':
            continue

        assignment_items.append({
            'assignment': assign,
            'submission': sub,
            'status': status
        })

    return render_template(
        'student/assignments.html',
        assignment_items=assignment_items,
        status_filter=status_filter,
        total_count=len(all_assignments),
        pending_count=sum(1 for a in all_assignments if a.id not in submissions and a.due_date >= now),
        submitted_count=sum(1 for a in all_assignments if a.id in submissions and submissions[a.id].marks_obtained is None),
        graded_count=sum(1 for a in all_assignments if a.id in submissions and submissions[a.id].marks_obtained is not None)
    )


@student_bp.route('/assignments/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@student_required
def assignment_detail(assignment_id):
    profile = current_user.student_profile
    assignment = Assignment.query.get_or_404(assignment_id)

    # Check if student is enrolled in this subject
    is_enrolled = Enrollment.query.filter_by(student_id=profile.id, subject_id=assignment.subject_id).first()
    if not is_enrolled:
        abort(403)

    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment.id,
        student_id=profile.id
    ).first()

    form = AssignmentSubmissionForm()
    if form.validate_on_submit():
        file_path = None
        if form.submission_file.data:
            file_path = save_uploaded_file(form.submission_file.data, 'submissions', 'all')
            if not file_path:
                flash('Invalid file format. Please upload PDF, Word document, ZIP or code files.', 'danger')
                return render_template('student/assignment_detail.html', assignment=assignment, submission=submission, form=form)

        if submission:
            # Updating existing submission
            submission.submission_text = form.submission_text.data
            if file_path:
                submission.file_path = file_path
            submission.submitted_at = datetime.utcnow()
            submission.status = 'Late' if datetime.utcnow() > assignment.due_date else 'Submitted'
            flash('Your submission has been updated successfully.', 'success')
        else:
            # New submission
            status = 'Late' if datetime.utcnow() > assignment.due_date else 'Submitted'
            submission = AssignmentSubmission(
                assignment_id=assignment.id,
                student_id=profile.id,
                submission_text=form.submission_text.data,
                file_path=file_path,
                status=status
            )
            db.session.add(submission)
            flash('Assignment submitted successfully!', 'success')

        db.session.commit()
        return redirect(url_for('student.assignment_detail', assignment_id=assignment.id))

    return render_template(
        'student/assignment_detail.html',
        assignment=assignment,
        submission=submission,
        form=form
    )


@student_bp.route('/examinations')
@login_required
@student_required
def examinations():
    profile = current_user.student_profile
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()
    subject_ids = [e.subject_id for e in enrollments]

    # Upcoming and past published exams
    today = date.today()
    upcoming_exams = Examination.query.filter(
        Examination.subject_id.in_(subject_ids) if subject_ids else False,
        Examination.exam_date >= today,
        Examination.is_published == True
    ).order_by(Examination.exam_date.asc(), Examination.start_time.asc()).all()

    past_exams = Examination.query.filter(
        Examination.subject_id.in_(subject_ids) if subject_ids else False,
        Examination.exam_date < today,
        Examination.is_published == True
    ).order_by(Examination.exam_date.desc()).all()

    # Results for student
    results = Result.query.join(Examination).filter(
        Result.student_id == profile.id,
        Result.is_published == True
    ).order_by(Examination.exam_date.desc()).all()

    # Aggregate result metrics
    total_obtained = sum(r.marks_obtained for r in results)
    total_max = sum(r.examination.max_marks for r in results)
    overall_percentage = round((total_obtained / total_max * 100), 2) if total_max > 0 else 0.0

    return render_template(
        'student/examinations.html',
        profile=profile,
        upcoming_exams=upcoming_exams,
        past_exams=past_exams,
        results=results,
        total_obtained=total_obtained,
        total_max=total_max,
        overall_percentage=overall_percentage
    )


@student_bp.route('/timetable')
@login_required
@student_required
def timetable():
    profile = current_user.student_profile
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Organize schedule by day
    schedule = {}
    for d in days:
        schedule[d] = TimetableEntry.query.filter_by(
            department_id=profile.department_id,
            semester=profile.semester,
            day_of_week=d
        ).order_by(TimetableEntry.start_time.asc()).all()

    current_day = datetime.now().strftime('%A')
    return render_template(
        'student/timetable.html',
        profile=profile,
        days=days,
        schedule=schedule,
        current_day=current_day
    )


@student_bp.route('/study-materials')
@login_required
@student_required
def study_materials():
    profile = current_user.student_profile
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()
    subject_ids = [e.subject_id for e in enrollments]

    # Filters
    search_query = request.args.get('q', '').strip()
    selected_subject = request.args.get('subject_id', type=int)
    selected_type = request.args.get('type', '').strip()

    query = StudyMaterial.query.filter(
        StudyMaterial.subject_id.in_(subject_ids) if subject_ids else False
    )

    if search_query:
        query = query.filter(StudyMaterial.title.ilike(f'%{search_query}%'))
    if selected_subject:
        query = query.filter_by(subject_id=selected_subject)
    if selected_type:
        query = query.filter_by(material_type=selected_type)

    materials = query.order_by(StudyMaterial.uploaded_at.desc()).all()
    enrolled_subjects = [db.session.get(Subject, sid) for sid in subject_ids if db.session.get(Subject, sid)]

    return render_template(
        'student/study_materials.html',
        materials=materials,
        subjects=enrolled_subjects,
        search_query=search_query,
        selected_subject=selected_subject,
        selected_type=selected_type
    )


@student_bp.route('/download/<folder>/<filename>')
@login_required
def download_file(folder, filename):
    # Only allow safe subfolders
    allowed_folders = {'materials', 'assignments', 'submissions', 'avatars'}
    if folder not in allowed_folders:
        abort(404)

    target_dir = Path(current_app.config['UPLOAD_FOLDER']) / folder
    return send_from_directory(str(target_dir), filename, as_attachment=True)


@student_bp.route('/announcements')
@login_required
@student_required
def announcements():
    profile = current_user.student_profile
    category = request.args.get('category', 'all')
    search = request.args.get('q', '').strip()

    query = Announcement.query.filter(
        (Announcement.department_id == profile.department_id) | (Announcement.department_id.is_(None))
    )

    if category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Announcement.title.ilike(f'%{search}%') | Announcement.content.ilike(f'%{search}%'))

    announcement_list = query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).all()

    return render_template(
        'student/announcements.html',
        announcements=announcement_list,
        current_category=category,
        search_query=search
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    student_profile = current_user.student_profile
    form = StudentProfileUpdateForm(obj=student_profile)
    pwd_form = ChangePasswordForm()

    if form.validate_on_submit():
        student_profile.phone = form.phone.data.strip() if form.phone.data else None
        student_profile.address = form.address.data.strip() if form.address.data else None
        student_profile.bio = form.bio.data.strip() if form.bio.data else None

        if form.avatar.data:
            avatar_path = save_uploaded_file(form.avatar.data, 'avatars', 'image')
            if avatar_path:
                student_profile.avatar = avatar_path.replace('avatars/', '')
            else:
                flash('Invalid image format for avatar. Use JPG, PNG, or WEBP.', 'warning')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    return render_template(
        'student/profile.html',
        profile=student_profile,
        form=form,
        pwd_form=pwd_form
    )


@student_bp.route('/notifications/read/<int:notif_id>')
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    if notif.link:
        return redirect(notif.link)
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('student.dashboard'))


@student_bp.route('/notifications/read-all')
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'info')
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('student.dashboard'))
