"""
seed.py - Seed Script for StudentHub
Populates database with realistic college departments, subjects, students,
administrators, timetable entries, attendance records, assignments,
examinations, study materials, and campus announcements.
"""

import os
from datetime import datetime, date, time, timedelta
from pathlib import Path
from app import create_app
from app.models import (
    db, User, StudentProfile, Department, Subject, Enrollment,
    AttendanceRecord, Assignment, AssignmentSubmission,
    Examination, Result, TimetableEntry, StudyMaterial,
    Announcement, Notification
)

app = create_app('development')

def seed_database():
    with app.app_context():
        # Clean existing database tables
        db.drop_all()
        db.create_all()
        print("[*] Database tables created successfully.")

        # Ensure upload folders and sample dummy files exist
        upload_folder = Path(app.config['UPLOAD_FOLDER'])
        materials_dir = upload_folder / 'materials'
        assignments_dir = upload_folder / 'assignments'
        materials_dir.mkdir(parents=True, exist_ok=True)
        assignments_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy sample materials so file downloads work seamlessly
        sample_doc_content = (
            "STUDENTHUB ACADEMIC DOCUMENT\n"
            "============================\n"
            "This is a verified academic resource file provided for student study.\n"
            "Topic: Comprehensive Course Notes & Reference Questions.\n"
            "StudentHub Smart Student Portal (c) 2026\n"
        )
        sample_mat_file = materials_dir / "dbms_unit1_notes.txt"
        with open(sample_mat_file, "w", encoding="utf-8") as f:
            f.write(sample_doc_content)

        sample_assign_file = assignments_dir / "er_diagram_spec.txt"
        with open(sample_assign_file, "w", encoding="utf-8") as f:
            f.write(sample_doc_content)

        # 1. Create Administrator Account
        admin_user = User(
            username='admin',
            email='admin@studenthub.edu',
            role='admin',
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.flush()
        print(f"[+] Administrator created: admin / admin123")

        # 2. Create Departments
        depts_data = [
            ('CSE', 'Computer Science & Engineering', 'Department of Computer Science and Software Engineering.'),
            ('IT', 'Information Technology', 'Department of Information Technology and Cloud Systems.'),
            ('ECE', 'Electronics & Communication', 'Department of Electronics and Signal Processing.'),
            ('ME', 'Mechanical Engineering', 'Department of Mechanical and Industrial Systems.')
        ]
        dept_models = {}
        for code, name, desc in depts_data:
            d = Department(code=code, name=name, description=desc)
            db.session.add(d)
            dept_models[code] = d
        db.session.flush()
        print(f"[+] Created {len(dept_models)} departments.")

        # 3. Create Subjects for CSE (Semester 5) and IT
        cse_dept = dept_models['CSE']
        it_dept = dept_models['IT']

        subjects_data = [
            # CSE Semester 5
            ('CS501', 'Database Management Systems', cse_dept.id, 5, 4, 'Prof. Alan Turing'),
            ('CS502', 'Computer Networks & Protocols', cse_dept.id, 5, 4, 'Dr. Radia Perlman'),
            ('CS503', 'Software Engineering & Agile', cse_dept.id, 5, 3, 'Prof. Margaret Hamilton'),
            ('CS504', 'Theory of Computation', cse_dept.id, 5, 3, 'Dr. Donald Knuth'),
            ('CS505', 'Web Development & Cloud Architecture', cse_dept.id, 5, 4, 'Prof. Tim Berners-Lee'),
            # IT Semester 3
            ('IT301', 'Data Structures & Algorithms', it_dept.id, 3, 4, 'Dr. Barbara Liskov'),
            ('IT302', 'Object Oriented Programming in Java', it_dept.id, 3, 4, 'Prof. James Gosling'),
            ('IT303', 'Digital Logic Design', it_dept.id, 3, 3, 'Dr. Claude Shannon')
        ]
        subject_models = {}
        for code, name, d_id, sem, credits, faculty in subjects_data:
            s = Subject(
                code=code,
                name=name,
                department_id=d_id,
                semester=sem,
                credits=credits,
                faculty_name=faculty
            )
            db.session.add(s)
            subject_models[code] = s
        db.session.flush()
        print(f"[+] Created {len(subject_models)} curriculum subjects.")

        # 4. Create Students
        students_data = [
            {
                'username': 'student1',
                'email': 'alex.morgan@campus.edu',
                'password': 'password123',
                'full_name': 'Alex Morgan',
                'student_id': 'STU2026001',
                'department_id': cse_dept.id,
                'semester': 5,
                'academic_year': '2025-2026',
                'phone': '+1 (555) 234-5678',
                'address': 'Dormitory Hall 4, Room 204, Campus Campus',
                'bio': 'Passionate computer science junior interested in database optimization and full-stack software development.'
            },
            {
                'username': 'student2',
                'email': 'sophia.chen@campus.edu',
                'password': 'password123',
                'full_name': 'Sophia Chen',
                'student_id': 'STU2026002',
                'department_id': cse_dept.id,
                'semester': 5,
                'academic_year': '2025-2026',
                'phone': '+1 (555) 876-5432',
                'address': 'Westfield Residency 12B, Metroville',
                'bio': 'Junior engineer exploring distributed networks, cloud architecture, and cyber defense.'
            },
            {
                'username': 'student3',
                'email': 'liam.johnson@campus.edu',
                'password': 'password123',
                'full_name': 'Liam Johnson',
                'student_id': 'STU2026003',
                'department_id': it_dept.id,
                'semester': 3,
                'academic_year': '2025-2026',
                'phone': '+1 (555) 345-6789',
                'address': 'North Campus Apartments, Unit 10',
                'bio': 'Sophomore IT student with keen focus on algorithms, data structures, and mobile app design.'
            }
        ]

        student_profiles = []
        for s_info in students_data:
            u = User(
                username=s_info['username'],
                email=s_info['email'],
                role='student',
                is_active=True
            )
            u.set_password(s_info['password'])
            db.session.add(u)
            db.session.flush()

            sp = StudentProfile(
                user_id=u.id,
                student_id=s_info['student_id'],
                full_name=s_info['full_name'],
                department_id=s_info['department_id'],
                semester=s_info['semester'],
                academic_year=s_info['academic_year'],
                phone=s_info['phone'],
                address=s_info['address'],
                bio=s_info['bio'],
                avatar='default-avatar.svg'
            )
            db.session.add(sp)
            student_profiles.append(sp)

        db.session.flush()
        print(f"[+] Created {len(student_profiles)} student accounts.")

        # 5. Enroll Students
        cse_subjects = [s for code, s in subject_models.items() if s.department_id == cse_dept.id]
        it_subjects = [s for code, s in subject_models.items() if s.department_id == it_dept.id]

        for sp in student_profiles:
            subjs = cse_subjects if sp.department_id == cse_dept.id else it_subjects
            for subj in subjs:
                enrollment = Enrollment(
                    student_id=sp.id,
                    subject_id=subj.id,
                    academic_year=sp.academic_year,
                    semester=sp.semester
                )
                db.session.add(enrollment)
        db.session.flush()

        # 6. Seed Attendance Records
        # Generate 15 distinct class dates over the past 3 weeks
        alex = student_profiles[0]
        today = date.today()
        dates_list = [(today - timedelta(days=i)) for i in range(1, 22) if (today - timedelta(days=i)).weekday() < 5][:15]

        for d in dates_list:
            for s in cse_subjects:
                # Let's create varying attendance so CS504 is under 75% for Alex to test warning!
                if s.code == 'CS504':
                    # 9 classes attended out of 15 => 60% (Triggers warning highlight!)
                    status = 'Present' if (d.day % 2 == 0 or d.day % 5 == 0) else 'Absent'
                elif s.code == 'CS501':
                    # 14 out of 15 => 93% (Excellent)
                    status = 'Absent' if d == dates_list[2] else 'Present'
                elif s.code == 'CS502':
                    status = 'Present' if d != dates_list[4] else 'Excused'
                else:
                    status = 'Present' if d.day % 7 != 0 else 'Absent'

                rec = AttendanceRecord(
                    student_id=alex.id,
                    subject_id=s.id,
                    date=d,
                    status=status,
                    remarks='Verified by Faculty' if status == 'Present' else ('Medical leave approved' if status == 'Excused' else 'Unexcused Absence'),
                    recorded_by=admin_user.id
                )
                db.session.add(rec)

        print("[+] Generated 75+ verified attendance records.")

        # 7. Seed Timetable for CSE Semester 5
        timetable_slots = [
            # Monday
            (cse_dept.id, 5, 'Monday', time(9, 0), time(10, 0), subject_models['CS501'].id, False, None, 'Hall 101', 'Prof. Alan Turing'),
            (cse_dept.id, 5, 'Monday', time(10, 0), time(11, 0), subject_models['CS502'].id, False, None, 'Hall 102', 'Dr. Radia Perlman'),
            (cse_dept.id, 5, 'Monday', time(11, 0), time(11, 30), None, True, 'Morning Recess', None, None),
            (cse_dept.id, 5, 'Monday', time(11, 30), time(12, 30), subject_models['CS503'].id, False, None, 'Hall 103', 'Prof. Margaret Hamilton'),
            (cse_dept.id, 5, 'Monday', time(12, 30), time(13, 30), None, True, 'Lunch Interval', None, None),
            (cse_dept.id, 5, 'Monday', time(13, 30), time(15, 30), subject_models['CS505'].id, False, None, 'Cloud Lab 2', 'Prof. Tim Berners-Lee'),

            # Tuesday
            (cse_dept.id, 5, 'Tuesday', time(9, 0), time(10, 0), subject_models['CS504'].id, False, None, 'Hall 104', 'Dr. Donald Knuth'),
            (cse_dept.id, 5, 'Tuesday', time(10, 0), time(11, 0), subject_models['CS501'].id, False, None, 'Hall 101', 'Prof. Alan Turing'),
            (cse_dept.id, 5, 'Tuesday', time(11, 0), time(11, 30), None, True, 'Morning Recess', None, None),
            (cse_dept.id, 5, 'Tuesday', time(11, 30), time(12, 30), subject_models['CS502'].id, False, None, 'Hall 102', 'Dr. Radia Perlman'),
            (cse_dept.id, 5, 'Tuesday', time(12, 30), time(13, 30), None, True, 'Lunch Interval', None, None),
            (cse_dept.id, 5, 'Tuesday', time(13, 30), time(14, 30), subject_models['CS503'].id, False, None, 'Hall 103', 'Prof. Margaret Hamilton'),

            # Wednesday
            (cse_dept.id, 5, 'Wednesday', time(9, 0), time(10, 0), subject_models['CS505'].id, False, None, 'Hall 201', 'Prof. Tim Berners-Lee'),
            (cse_dept.id, 5, 'Wednesday', time(10, 0), time(11, 0), subject_models['CS504'].id, False, None, 'Hall 104', 'Dr. Donald Knuth'),
            (cse_dept.id, 5, 'Wednesday', time(11, 0), time(11, 30), None, True, 'Morning Recess', None, None),
            (cse_dept.id, 5, 'Wednesday', time(11, 30), time(13, 30), subject_models['CS501'].id, False, None, 'Database Lab 1', 'Prof. Alan Turing'),

            # Thursday
            (cse_dept.id, 5, 'Thursday', time(9, 0), time(10, 0), subject_models['CS502'].id, False, None, 'Hall 102', 'Dr. Radia Perlman'),
            (cse_dept.id, 5, 'Thursday', time(10, 0), time(11, 0), subject_models['CS503'].id, False, None, 'Hall 103', 'Prof. Margaret Hamilton'),
            (cse_dept.id, 5, 'Thursday', time(11, 0), time(11, 30), None, True, 'Morning Recess', None, None),
            (cse_dept.id, 5, 'Thursday', time(11, 30), time(12, 30), subject_models['CS504'].id, False, None, 'Hall 104', 'Dr. Donald Knuth'),
            (cse_dept.id, 5, 'Thursday', time(12, 30), time(13, 30), None, True, 'Lunch Interval', None, None),

            # Friday
            (cse_dept.id, 5, 'Friday', time(9, 0), time(10, 0), subject_models['CS505'].id, False, None, 'Hall 201', 'Prof. Tim Berners-Lee'),
            (cse_dept.id, 5, 'Friday', time(10, 0), time(11, 0), subject_models['CS501'].id, False, None, 'Hall 101', 'Prof. Alan Turing'),
            (cse_dept.id, 5, 'Friday', time(11, 0), time(11, 30), None, True, 'Morning Recess', None, None),
            (cse_dept.id, 5, 'Friday', time(11, 30), time(12, 30), subject_models['CS502'].id, False, None, 'Hall 102', 'Dr. Radia Perlman')
        ]

        for dept_id, sem, day, st, et, sub_id, is_brk, brk_title, room, fac in timetable_slots:
            slot = TimetableEntry(
                department_id=dept_id,
                semester=sem,
                day_of_week=day,
                start_time=st,
                end_time=et,
                subject_id=sub_id,
                is_break=is_brk,
                break_title=brk_title,
                classroom=room,
                faculty_name=fac
            )
            db.session.add(slot)
        print("[+] Created weekly timetable entries.")

        # 8. Seed Coursework Assignments & Submissions
        now = datetime.utcnow()
        assignments_data = [
            {
                'subject': subject_models['CS501'],
                'title': 'Assignment 1: Relational Schema & 3NF Normalization',
                'description': 'Design an entity-relationship model and decompose tables up to Boyce-Codd Normal Form (BCNF) for an e-commerce platform.',
                'due_date': now + timedelta(days=5, hours=4),
                'max_marks': 100.0,
                'file_attachment': 'assignments/er_diagram_spec.txt'
            },
            {
                'subject': subject_models['CS502'],
                'title': 'Assignment 2: TCP vs UDP Socket Programming',
                'description': 'Implement client-server communication using multi-threaded BSD sockets in Python or C. Handle packet loss simulation.',
                'due_date': now + timedelta(days=9, hours=2),
                'max_marks': 50.0,
                'file_attachment': None
            },
            {
                'subject': subject_models['CS505'],
                'title': 'Project Milestone 1: REST API Architecture',
                'description': 'Develop RESTful endpoints with authentication and JWT tokens. Document OpenAPI schema.',
                'due_date': now - timedelta(days=3),
                'max_marks': 100.0,
                'file_attachment': None
            }
        ]

        created_assignments = []
        for a_dict in assignments_data:
            a = Assignment(
                subject_id=a_dict['subject'].id,
                title=a_dict['title'],
                description=a_dict['description'],
                due_date=a_dict['due_date'],
                max_marks=a_dict['max_marks'],
                file_attachment=a_dict['file_attachment'],
                created_by=admin_user.id
            )
            db.session.add(a)
            created_assignments.append(a)
        db.session.flush()

        # Add Alex's submission for Project Milestone 1 (Graded)
        sub1 = AssignmentSubmission(
            assignment_id=created_assignments[2].id,
            student_id=alex.id,
            submission_text='GitHub Repository: https://github.com/alexmorgan/studenthub-rest-api\nAll test suites passing with 98% coverage.',
            submitted_at=now - timedelta(days=4),
            status='Graded',
            marks_obtained=94.0,
            feedback='Outstanding implementation! Clean error handling and thorough unit tests.',
            graded_at=now - timedelta(days=2),
            graded_by=admin_user.id
        )
        db.session.add(sub1)

        # 9. Seed Examinations and Results
        exams_data = [
            # Upcoming Exams
            (subject_models['CS501'], 'Mid-Term Examination 2026', today + timedelta(days=7), time(10, 0), time(12, 0), 'Auditorium Hall A', 100.0, 40.0, True),
            (subject_models['CS502'], 'Mid-Term Examination 2026', today + timedelta(days=9), time(10, 0), time(12, 0), 'Hall B-201', 100.0, 40.0, True),
            (subject_models['CS503'], 'Mid-Term Examination 2026', today + timedelta(days=12), time(14, 0), time(16, 0), 'Auditorium Hall A', 100.0, 40.0, True),
            (subject_models['CS505'], 'Mid-Term Practical Assessment', today + timedelta(days=15), time(9, 30), time(12, 30), 'Cloud Systems Lab', 50.0, 20.0, True),
            # Past exam for result scorecard demonstration
            (subject_models['CS501'], 'Unit Assessment 1 (Internal)', today - timedelta(days=20), time(10, 0), time(11, 30), 'Hall 101', 50.0, 20.0, True),
            (subject_models['CS502'], 'Unit Assessment 1 (Internal)', today - timedelta(days=18), time(10, 0), time(11, 30), 'Hall 102', 50.0, 20.0, True)
        ]

        created_exams = []
        for subj, name, dt, st, et, venue, max_m, pass_m, pub in exams_data:
            ex = Examination(
                subject_id=subj.id,
                exam_name=name,
                exam_date=dt,
                start_time=st,
                end_time=et,
                venue=venue,
                max_marks=max_m,
                passing_marks=pass_m,
                academic_year='2025-2026',
                semester=subj.semester,
                is_published=pub
            )
            db.session.add(ex)
            created_exams.append(ex)
        db.session.flush()

        # Add Results for Alex for past exams
        res1 = Result(
            examination_id=created_exams[4].id,
            student_id=alex.id,
            marks_obtained=46.5,
            grade='A+',
            remarks='Excellent query formulation and relational algebra proofs.',
            is_published=True,
            published_at=datetime.utcnow() - timedelta(days=15)
        )
        res2 = Result(
            examination_id=created_exams[5].id,
            student_id=alex.id,
            marks_obtained=42.0,
            grade='A',
            remarks='Great grasp of OSI 7-layer stack and subnetting.',
            is_published=True,
            published_at=datetime.utcnow() - timedelta(days=14)
        )
        db.session.add_all([res1, res2])

        # 10. Seed Study Materials
        materials_data = [
            (subject_models['CS501'], 'Unit 1: Relational Database Model & SQL Cheatsheet', 'Lecture Notes', 'dbms_unit1_notes.txt'),
            (subject_models['CS501'], 'DBMS Previous 5 Years Question Papers (2020-2025)', 'Previous Question Paper', 'dbms_unit1_notes.txt'),
            (subject_models['CS502'], 'Computer Networks Complete Syllabus & Lab Manual', 'Syllabus', 'dbms_unit1_notes.txt'),
            (subject_models['CS503'], 'Agile Software Engineering Methodology Handbook', 'Reference Book', 'dbms_unit1_notes.txt'),
            (subject_models['CS505'], 'Full-Stack Web Development Course Slides (Deck 1-8)', 'Lecture Notes', 'dbms_unit1_notes.txt')
        ]
        for subj, title, m_type, f_name in materials_data:
            sm = StudyMaterial(
                subject_id=subj.id,
                title=title,
                description=f'Official course material verified for {subj.name} by faculty.',
                material_type=m_type,
                file_path=f_name,
                file_size_kb=124,
                uploaded_by=admin_user.id
            )
            db.session.add(sm)

        # 11. Seed Campus Announcements
        announcements_data = [
            ('Mid-Term Examination Schedule Published',
             'The comprehensive timetable for the Fall Semester 2026 Mid-Term Examinations is now live. Please review your hall allocations and reporting times.',
             'Examination', 'Urgent', None, True),
            ('Annual Hackathon & Tech Symposium 2026 Registration Open',
             'Registration for HackSphere 2026 has opened for all engineering and IT students. Form your 3-4 member teams and submit project pitches by next Friday.',
             'Event', 'Important', None, True),
            ('Campus Library Extended Study Hours During Exam Weeks',
             'The Central Academic Library will remain open 24/7 starting Monday through the completion of Mid-Term Examinations.',
             'Academic', 'Normal', None, False),
            ('National Holiday Notice — Campus Closed',
             'The college campus and academic offices will remain closed on the upcoming Monday in observance of Founder Day.',
             'Holiday', 'Normal', None, False),
            ('CSE Department Guest Lecture: Distributed Systems at Scale',
             'Special industry lecture by Google Cloud Principal Architect this Thursday at 3:00 PM in the Main Auditorium.',
             'Department', 'Important', cse_dept.id, False)
        ]
        for title, content, cat, prio, dep_id, pinned in announcements_data:
            ann = Announcement(
                title=title,
                content=content,
                category=cat,
                priority=prio,
                department_id=dep_id,
                is_pinned=pinned,
                created_by=admin_user.id
            )
            db.session.add(ann)

        # 12. Seed Notifications for Alex
        notifications_data = [
            ('New Assignment Published', 'Assignment 1: Relational Schema & 3NF Normalization has been posted for CS501.', '/student/assignments'),
            ('Score Released', 'Your submission for Project Milestone 1: REST API Architecture has been graded: 94.0/100.', '/student/assignments'),
            ('Exam Notice', 'Mid-Term Examination Schedule for Semester 5 has been published.', '/student/examinations')
        ]
        for title, msg, link in notifications_data:
            notif = Notification(
                user_id=alex.user.id,
                title=title,
                message=msg,
                link=link,
                is_read=False
            )
            db.session.add(notif)

        db.session.commit()
        print("[+] All sample academic data committed successfully!")
        print("\n=======================================================")
        print("  StudentHub Database Initialized Successfully!      ")
        print("=======================================================")
        print("  Demo Credentials:                                    ")
        print("  - Student:  Username: student1  | Password: password123")
        print("  - Admin:    Username: admin     | Password: admin123   ")
        print("=======================================================\n")

if __name__ == '__main__':
    seed_database()
