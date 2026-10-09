from datetime import datetime, date
from pathlib import Path
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import current_user, login_required
from app.admin import admin_bp
from app.models import (
    db, User, StudentProfile, Department, Subject, Enrollment,
    AttendanceRecord, Assignment, AssignmentSubmission,
    Examination, Result, TimetableEntry, StudyMaterial,
    Announcement, Notification
)
from app.forms import (
    DepartmentForm, SubjectForm, AssignmentForm, GradeSubmissionForm,
    ExaminationForm, ResultForm, TimetableEntryForm, StudyMaterialForm,
    AnnouncementForm
)
from app.utils import admin_required, save_uploaded_file, calculate_grade, send_notification


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_students = StudentProfile.query.count()
    total_departments = Department.query.count()
    total_subjects = Subject.query.count()
    total_assignments = Assignment.query.count()
    total_announcements = Announcement.query.count()

    # Submissions pending grading
    pending_submissions = AssignmentSubmission.query.filter(
        AssignmentSubmission.marks_obtained.is_(None)
    ).count()

    # Campus overall attendance
    total_attendance_records = AttendanceRecord.query.count()
    present_records = AttendanceRecord.query.filter_by(status='Present').count()
    avg_attendance = round((present_records / total_attendance_records * 100), 1) if total_attendance_records > 0 else 0.0

    recent_students = StudentProfile.query.order_by(StudentProfile.created_at.desc()).limit(5).all()
    recent_submissions = AssignmentSubmission.query.order_by(AssignmentSubmission.submitted_at.desc()).limit(5).all()

    # Department student distribution for chart
    departments = Department.query.all()
    dept_chart_data = [{
        'name': d.code,
        'count': d.students.count()
    } for d in departments]

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_departments=total_departments,
        total_subjects=total_subjects,
        total_assignments=total_assignments,
        total_announcements=total_announcements,
        pending_submissions=pending_submissions,
        avg_attendance=avg_attendance,
        recent_students=recent_students,
        recent_submissions=recent_submissions,
        dept_chart_data=dept_chart_data
    )


# ----------------- STUDENT MANAGEMENT ----------------- #

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    search = request.args.get('q', '').strip()
    dept_id = request.args.get('dept_id', type=int)
    sem = request.args.get('sem', type=int)

    query = StudentProfile.query.join(User)

    if search:
        query = query.filter(
            (StudentProfile.full_name.ilike(f'%{search}%')) |
            (StudentProfile.student_id.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    if dept_id:
        query = query.filter(StudentProfile.department_id == dept_id)
    if sem:
        query = query.filter(StudentProfile.semester == sem)

    students_list = query.order_by(StudentProfile.student_id.asc()).all()
    departments = Department.query.order_by(Department.name).all()

    return render_template(
        'admin/students.html',
        students=students_list,
        departments=departments,
        search_query=search,
        selected_dept=dept_id,
        selected_sem=sem
    )


@admin_bp.route('/students/<int:student_id>')
@login_required
@admin_required
def student_detail(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    attendance_records = AttendanceRecord.query.filter_by(student_id=student.id).all()
    results = Result.query.filter_by(student_id=student.id).all()
    submissions = AssignmentSubmission.query.filter_by(student_id=student.id).all()

    total_classes = len(attendance_records)
    present_classes = sum(1 for a in attendance_records if a.status == 'Present')
    attendance_pct = round((present_classes / total_classes * 100), 1) if total_classes > 0 else 0.0

    return render_template(
        'admin/student_detail.html',
        student=student,
        enrollments=enrollments,
        total_classes=total_classes,
        present_classes=present_classes,
        attendance_pct=attendance_pct,
        results=results,
        submissions=submissions
    )


@admin_bp.route('/students/<int:student_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_student_status(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    user = student.user
    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    flash(f'Student account {student.student_id} has been {status_str}.', 'info')
    return redirect(url_for('admin.students'))


# ----------------- DEPARTMENTS ----------------- #

@admin_bp.route('/departments', methods=['GET', 'POST'])
@login_required
@admin_required
def departments():
    form = DepartmentForm()
    if form.validate_on_submit():
        existing = Department.query.filter_by(code=form.code.data.strip().upper()).first()
        if existing:
            flash(f'Department code {form.code.data.upper()} already exists.', 'warning')
        else:
            dept = Department(
                code=form.code.data.strip().upper(),
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None
            )
            db.session.add(dept)
            db.session.commit()
            flash(f'Department {dept.name} added successfully!', 'success')
            return redirect(url_for('admin.departments'))

    departments_list = Department.query.order_by(Department.name).all()
    return render_template('admin/departments.html', form=form, departments=departments_list)


@admin_bp.route('/departments/<int:dept_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    if dept.students.count() > 0 or dept.subjects.count() > 0:
        flash('Cannot delete department with associated students or courses.', 'danger')
        return redirect(url_for('admin.departments'))
    db.session.delete(dept)
    db.session.commit()
    flash('Department deleted.', 'info')
    return redirect(url_for('admin.departments'))


# ----------------- SUBJECTS ----------------- #

@admin_bp.route('/subjects', methods=['GET', 'POST'])
@login_required
@admin_required
def subjects():
    form = SubjectForm()
    depts = Department.query.order_by(Department.name).all()
    form.department_id.choices = [(d.id, f"{d.name} ({d.code})") for d in depts]

    if form.validate_on_submit():
        existing = Subject.query.filter_by(code=form.code.data.strip().upper()).first()
        if existing:
            flash(f'Subject code {form.code.data.upper()} already exists.', 'warning')
        else:
            subj = Subject(
                code=form.code.data.strip().upper(),
                name=form.name.data.strip(),
                department_id=form.department_id.data,
                semester=form.semester.data,
                credits=form.credits.data,
                faculty_name=form.faculty_name.data.strip()
            )
            db.session.add(subj)
            db.session.commit()
            flash(f'Subject {subj.name} added successfully!', 'success')
            return redirect(url_for('admin.subjects'))

    subjects_list = Subject.query.order_by(Subject.department_id, Subject.semester, Subject.code).all()
    return render_template('admin/subjects.html', form=form, subjects=subjects_list)


@admin_bp.route('/subjects/<int:subj_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_subject(subj_id):
    subj = Subject.query.get_or_404(subj_id)
    db.session.delete(subj)
    db.session.commit()
    flash('Subject deleted.', 'info')
    return redirect(url_for('admin.subjects'))


# ----------------- ATTENDANCE MANAGEMENT ----------------- #

@admin_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
@admin_required
def attendance():
    depts = Department.query.order_by(Department.name).all()
    selected_dept_id = request.args.get('dept_id', type=int) or (depts[0].id if depts else None)
    selected_sem = request.args.get('sem', 1, type=int)
    
    subjects_in_scope = Subject.query.filter_by(
        department_id=selected_dept_id,
        semester=selected_sem
    ).all() if selected_dept_id else []

    selected_subject_id = request.args.get('subject_id', type=int) or (subjects_in_scope[0].id if subjects_in_scope else None)
    selected_date_str = request.args.get('date', date.today().isoformat())

    try:
        attendance_date = date.fromisoformat(selected_date_str)
    except ValueError:
        attendance_date = date.today()

    students_in_scope = []
    if selected_dept_id and selected_sem:
        students_in_scope = StudentProfile.query.filter_by(
            department_id=selected_dept_id,
            semester=selected_sem
        ).order_by(StudentProfile.student_id).all()

    # Existing records for this subject and date
    existing_records = {}
    if selected_subject_id:
        records = AttendanceRecord.query.filter_by(
            subject_id=selected_subject_id,
            date=attendance_date
        ).all()
        existing_records = {r.student_id: r for r in records}

    if request.method == 'POST':
        if not selected_subject_id:
            flash('Please select a subject to record attendance.', 'danger')
            return redirect(request.url)

        saved_count = 0
        for student in students_in_scope:
            status_val = request.form.get(f'status_{student.id}', 'Present')
            remarks_val = request.form.get(f'remarks_{student.id}', '').strip()

            record = existing_records.get(student.id)
            if record:
                record.status = status_val
                record.remarks = remarks_val
                record.recorded_by = current_user.id
            else:
                record = AttendanceRecord(
                    student_id=student.id,
                    subject_id=selected_subject_id,
                    date=attendance_date,
                    status=status_val,
                    remarks=remarks_val,
                    recorded_by=current_user.id
                )
                db.session.add(record)
            saved_count += 1

        db.session.commit()
        flash(f'Attendance recorded for {saved_count} students on {attendance_date}.', 'success')
        return redirect(url_for('admin.attendance', dept_id=selected_dept_id, sem=selected_sem, subject_id=selected_subject_id, date=attendance_date.isoformat()))

    return render_template(
        'admin/attendance.html',
        departments=depts,
        selected_dept_id=selected_dept_id,
        selected_sem=selected_sem,
        subjects=subjects_in_scope,
        selected_subject_id=selected_subject_id,
        attendance_date=attendance_date,
        students=students_in_scope,
        existing_records=existing_records
    )


# ----------------- ASSIGNMENT MANAGEMENT ----------------- #

@admin_bp.route('/assignments', methods=['GET', 'POST'])
@login_required
@admin_required
def assignments():
    form = AssignmentForm()
    subjects_all = Subject.query.order_by(Subject.name).all()
    form.subject_id.choices = [(s.id, f"{s.code} - {s.name}") for s in subjects_all]

    if form.validate_on_submit():
        attachment_path = None
        if form.attachment.data:
            attachment_path = save_uploaded_file(form.attachment.data, 'assignments', 'all')

        try:
            due_dt = datetime.fromisoformat(form.due_date.data)
        except ValueError:
            due_dt = datetime.utcnow()

        assignment = Assignment(
            subject_id=form.subject_id.data,
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            file_attachment=attachment_path,
            due_date=due_dt,
            max_marks=form.max_marks.data,
            created_by=current_user.id
        )
        db.session.add(assignment)
        db.session.flush()

        # Notify enrolled students
        enrollments = Enrollment.query.filter_by(subject_id=assignment.subject_id).all()
        for e in enrollments:
            student = e.student
            if student and student.user:
                send_notification(
                    user_id=student.user.id,
                    title='New Assignment Posted',
                    message=f'New assignment "{assignment.title}" has been assigned for {assignment.subject.name}. Due: {assignment.due_date.strftime("%b %d, %Y")}',
                    link=url_for('student.assignment_detail', assignment_id=assignment.id)
                )

        db.session.commit()
        flash('Assignment published successfully and students notified!', 'success')
        return redirect(url_for('admin.assignments'))

    assignments_list = Assignment.query.order_by(Assignment.created_at.desc()).all()
    return render_template('admin/assignments.html', form=form, assignments=assignments_list)


@admin_bp.route('/assignments/<int:assign_id>/submissions', methods=['GET', 'POST'])
@login_required
@admin_required
def assignment_submissions(assign_id):
    assignment = Assignment.query.get_or_404(assign_id)
    grade_form = GradeSubmissionForm()

    if grade_form.validate_on_submit() and request.method == 'POST':
        submission_id = request.form.get('submission_id', type=int)
        submission = AssignmentSubmission.query.get_or_404(submission_id)
        submission.marks_obtained = grade_form.marks_obtained.data
        submission.feedback = grade_form.feedback.data.strip() if grade_form.feedback.data else None
        submission.graded_at = datetime.utcnow()
        submission.graded_by = current_user.id
        submission.status = 'Graded'

        if submission.student and submission.student.user:
            send_notification(
                user_id=submission.student.user.id,
                title='Assignment Graded',
                message=f'Your submission for "{assignment.title}" has been graded: {submission.marks_obtained}/{assignment.max_marks}',
                link=url_for('student.assignment_detail', assignment_id=assignment.id)
            )

        db.session.commit()
        flash('Grade and feedback saved successfully!', 'success')
        return redirect(url_for('admin.assignment_submissions', assign_id=assign_id))

    submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment.id).all()
    return render_template(
        'admin/assignment_submissions.html',
        assignment=assignment,
        submissions=submissions,
        grade_form=grade_form
    )


@admin_bp.route('/assignments/<int:assign_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_assignment(assign_id):
    assign = Assignment.query.get_or_404(assign_id)
    db.session.delete(assign)
    db.session.commit()
    flash('Assignment deleted successfully.', 'info')
    return redirect(url_for('admin.assignments'))


# ----------------- EXAMINATIONS & RESULTS ----------------- #

@admin_bp.route('/examinations', methods=['GET', 'POST'])
@login_required
@admin_required
def examinations():
    form = ExaminationForm()
    subjects_all = Subject.query.order_by(Subject.name).all()
    form.subject_id.choices = [(s.id, f"{s.code} - {s.name}") for s in subjects_all]

    if form.validate_on_submit():
        exam = Examination(
            subject_id=form.subject_id.data,
            exam_name=form.exam_name.data.strip(),
            exam_date=form.exam_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            venue=form.venue.data.strip(),
            max_marks=form.max_marks.data,
            passing_marks=form.passing_marks.data,
            academic_year=form.academic_year.data.strip(),
            semester=form.semester.data,
            is_published=form.is_published.data
        )
        db.session.add(exam)
        db.session.commit()
        flash(f'Examination "{exam.exam_name}" scheduled successfully.', 'success')
        return redirect(url_for('admin.examinations'))

    exams_list = Examination.query.order_by(Examination.exam_date.desc()).all()
    return render_template('admin/examinations.html', form=form, examinations=exams_list)


@admin_bp.route('/examinations/<int:exam_id>/toggle-publish', methods=['POST'])
@login_required
@admin_required
def toggle_exam_publish(exam_id):
    exam = Examination.query.get_or_404(exam_id)
    exam.is_published = not exam.is_published
    db.session.commit()
    state = "published" if exam.is_published else "hidden"
    flash(f'Examination schedule is now {state} to students.', 'info')
    return redirect(url_for('admin.examinations'))


@admin_bp.route('/examinations/<int:exam_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_examination(exam_id):
    exam = Examination.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    flash('Examination deleted.', 'info')
    return redirect(url_for('admin.examinations'))


@admin_bp.route('/results', methods=['GET', 'POST'])
@login_required
@admin_required
def results():
    form = ResultForm()
    exams = Examination.query.order_by(Examination.exam_date.desc()).all()
    students = StudentProfile.query.order_by(StudentProfile.student_id).all()

    form.examination_id.choices = [(e.id, f"{e.exam_name} - {e.subject.code}") for e in exams]
    form.student_id.choices = [(s.id, f"{s.student_id} - {s.full_name}") for s in students]

    if form.validate_on_submit():
        exam = Examination.query.get(form.examination_id.data)
        grade = calculate_grade(form.marks_obtained.data, exam.max_marks)

        existing = Result.query.filter_by(
            examination_id=form.examination_id.data,
            student_id=form.student_id.data
        ).first()

        if existing:
            existing.marks_obtained = form.marks_obtained.data
            existing.grade = grade
            existing.remarks = form.remarks.data.strip() if form.remarks.data else None
            existing.is_published = form.is_published.data
            if form.is_published.data and not existing.published_at:
                existing.published_at = datetime.utcnow()
            flash('Result updated successfully.', 'success')
        else:
            result = Result(
                examination_id=form.examination_id.data,
                student_id=form.student_id.data,
                marks_obtained=form.marks_obtained.data,
                grade=grade,
                remarks=form.remarks.data.strip() if form.remarks.data else None,
                is_published=form.is_published.data,
                published_at=datetime.utcnow() if form.is_published.data else None
            )
            db.session.add(result)
            flash('Result saved successfully.', 'success')

        # Send notification to student if published
        if form.is_published.data:
            stu = StudentProfile.query.get(form.student_id.data)
            if stu and stu.user:
                send_notification(
                    user_id=stu.user.id,
                    title='Exam Result Published',
                    message=f'Results for {exam.exam_name} ({exam.subject.name}) have been published.',
                    link=url_for('student.examinations')
                )

        db.session.commit()
        return redirect(url_for('admin.results'))

    results_list = Result.query.order_by(Result.created_at.desc()).all()
    return render_template('admin/results.html', form=form, results=results_list)


@admin_bp.route('/results/<int:result_id>/toggle-publish', methods=['POST'])
@login_required
@admin_required
def toggle_result_publish(result_id):
    res = Result.query.get_or_404(result_id)
    res.is_published = not res.is_published
    if res.is_published:
        res.published_at = datetime.utcnow()
    db.session.commit()
    flash('Result publish state updated.', 'info')
    return redirect(url_for('admin.results'))


# ----------------- TIMETABLE MANAGEMENT ----------------- #

@admin_bp.route('/timetable', methods=['GET', 'POST'])
@login_required
@admin_required
def timetable():
    form = TimetableEntryForm()
    depts = Department.query.order_by(Department.name).all()
    form.department_id.choices = [(d.id, f"{d.name} ({d.code})") for d in depts]
    
    subjects_all = Subject.query.order_by(Subject.name).all()
    form.subject_id.choices = [(0, '-- None / Break Period --')] + [(s.id, f"{s.code} - {s.name}") for s in subjects_all]

    if form.validate_on_submit():
        subj_id = form.subject_id.data if (form.subject_id.data and form.subject_id.data > 0 and not form.is_break.data) else None
        entry = TimetableEntry(
            department_id=form.department_id.data,
            semester=form.semester.data,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            is_break=form.is_break.data,
            break_title=form.break_title.data.strip() if form.is_break.data else None,
            subject_id=subj_id,
            classroom=form.classroom.data.strip() if form.classroom.data else None,
            faculty_name=form.faculty_name.data.strip() if form.faculty_name.data else None
        )
        db.session.add(entry)
        db.session.commit()
        flash('Timetable slot added successfully.', 'success')
        return redirect(url_for('admin.timetable', dept_id=form.department_id.data, sem=form.semester.data))

    selected_dept = request.args.get('dept_id', type=int) or (depts[0].id if depts else None)
    selected_sem = request.args.get('sem', 1, type=int)
    entries = TimetableEntry.query.filter_by(
        department_id=selected_dept,
        semester=selected_sem
    ).order_by(TimetableEntry.day_of_week, TimetableEntry.start_time).all()

    return render_template(
        'admin/timetable.html',
        form=form,
        departments=depts,
        selected_dept=selected_dept,
        selected_sem=selected_sem,
        entries=entries
    )


@admin_bp.route('/timetable/<int:entry_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_timetable_entry(entry_id):
    entry = TimetableEntry.query.get_or_404(entry_id)
    dept_id = entry.department_id
    sem = entry.semester
    db.session.delete(entry)
    db.session.commit()
    flash('Timetable entry deleted.', 'info')
    return redirect(url_for('admin.timetable', dept_id=dept_id, sem=sem))


# ----------------- STUDY MATERIALS ----------------- #

@admin_bp.route('/study-materials', methods=['GET', 'POST'])
@login_required
@admin_required
def study_materials():
    form = StudyMaterialForm()
    subjects_all = Subject.query.order_by(Subject.name).all()
    form.subject_id.choices = [(s.id, f"{s.code} - {s.name}") for s in subjects_all]

    if form.validate_on_submit():
        file_path = save_uploaded_file(form.file.data, 'materials', 'all')
        if not file_path:
            flash('Error uploading file. Allowed formats: PDF, DOC, PPT, ZIP, TXT.', 'danger')
        else:
            material = StudyMaterial(
                subject_id=form.subject_id.data,
                title=form.title.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                material_type=form.material_type.data,
                file_path=file_path.replace('materials/', ''),
                file_size_kb=0,
                uploaded_by=current_user.id
            )
            db.session.add(material)
            db.session.commit()
            flash('Study material uploaded successfully!', 'success')
            return redirect(url_for('admin.study_materials'))

    materials = StudyMaterial.query.order_by(StudyMaterial.uploaded_at.desc()).all()
    return render_template('admin/study_materials.html', form=form, materials=materials)


@admin_bp.route('/study-materials/<int:material_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_study_material(material_id):
    mat = StudyMaterial.query.get_or_404(material_id)
    db.session.delete(mat)
    db.session.commit()
    flash('Study material deleted.', 'info')
    return redirect(url_for('admin.study_materials'))


# ----------------- ANNOUNCEMENTS ----------------- #

@admin_bp.route('/announcements', methods=['GET', 'POST'])
@login_required
@admin_required
def announcements():
    form = AnnouncementForm()
    depts = Department.query.order_by(Department.name).all()
    form.department_id.choices = [(0, '-- Campus-wide (All Students) --')] + [(d.id, d.name) for d in depts]

    if form.validate_on_submit():
        dept_id = form.department_id.data if (form.department_id.data and form.department_id.data > 0) else None
        announcement = Announcement(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            category=form.category.data,
            priority=form.priority.data,
            department_id=dept_id,
            is_pinned=form.is_pinned.data,
            created_by=current_user.id
        )
        db.session.add(announcement)
        db.session.flush()

        # Send notifications to students
        if dept_id:
            students = StudentProfile.query.filter_by(department_id=dept_id).all()
        else:
            students = StudentProfile.query.all()

        for s in students:
            if s.user:
                send_notification(
                    user_id=s.user.id,
                    title=f"Notice: {announcement.title}",
                    message=f"[{announcement.category}] {announcement.title}",
                    link=url_for('student.announcements')
                )

        db.session.commit()
        flash('Announcement published and notifications delivered!', 'success')
        return redirect(url_for('admin.announcements'))

    announcements_list = Announcement.query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', form=form, announcements=announcements_list)


@admin_bp.route('/announcements/<int:ann_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted.', 'info')
    return redirect(url_for('admin.announcements'))
