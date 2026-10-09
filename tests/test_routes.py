def test_student_routes_accessible(client):
    # Log in as student
    client.post('/auth/login', data={
        'login_id': 'student1',
        'password': 'password123'
    }, follow_redirects=True)

    # Test dashboard
    resp = client.get('/student/dashboard')
    assert resp.status_code == 200

    # Test attendance
    resp = client.get('/student/attendance')
    assert resp.status_code == 200
    assert b'Attendance Record' in resp.data

    # Test assignments
    resp = client.get('/student/assignments')
    assert resp.status_code == 200
    assert b'Course Assignments' in resp.data

    # Test timetable
    resp = client.get('/student/timetable')
    assert resp.status_code == 200
    assert b'Weekly Class Schedule' in resp.data

    # Test examinations
    resp = client.get('/student/examinations')
    assert resp.status_code == 200

    # Test study materials
    resp = client.get('/student/study-materials')
    assert resp.status_code == 200

    # Test announcements
    resp = client.get('/student/announcements')
    assert resp.status_code == 200

    # Test profile
    resp = client.get('/student/profile')
    assert resp.status_code == 200
    assert b'Test Student' in resp.data


def test_admin_routes_accessible(client):
    # Log in as admin
    client.post('/auth/login', data={
        'login_id': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)

    # Test admin dashboard
    resp = client.get('/admin/dashboard')
    assert resp.status_code == 200
    assert b'Administrative Control Center' in resp.data

    # Test student directory
    resp = client.get('/admin/students')
    assert resp.status_code == 200
    assert b'STU2026001' in resp.data

    # Test departments
    resp = client.get('/admin/departments')
    assert resp.status_code == 200
    assert b'Computer Science' in resp.data

    # Test subjects
    resp = client.get('/admin/subjects')
    assert resp.status_code == 200
    assert b'CS101' in resp.data
