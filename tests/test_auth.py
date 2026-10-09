def test_password_hashing(app):
    from app.models import User
    u = User(username='hash_test', email='hash@test.com')
    u.set_password('mysecretpass')
    assert u.password_hash != 'mysecretpass'
    assert u.check_password('mysecretpass') is True
    assert u.check_password('wrongpass') is False


def test_login_success_student(client):
    response = client.post('/auth/login', data={
        'login_id': 'student1',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'StudentHub' in response.data
    assert b'Test Student' in response.data or b'Dashboard' in response.data


def test_login_invalid_password(client):
    response = client.post('/auth/login', data={
        'login_id': 'student1',
        'password': 'badpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username/email or password' in response.data


def test_login_success_admin(client):
    response = client.post('/auth/login', data={
        'login_id': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Administrative Control Center' in response.data or b'Dashboard' in response.data


def test_unauthorized_admin_access_by_student(client):
    # Log in as student
    client.post('/auth/login', data={
        'login_id': 'student1',
        'password': 'password123'
    }, follow_redirects=True)

    # Attempt to access admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 403


def test_unauthenticated_redirect(client):
    response = client.get('/student/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']
