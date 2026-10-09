import os
import uuid
from functools import wraps
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import abort, flash, redirect, url_for, current_app
from flask_login import current_user
from app.models import db, Notification


def admin_required(f):
    """Decorator to enforce administrator role access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to enforce student role access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_student:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename: str, category: str = 'document') -> bool:
    """Check whether the uploaded file extension is allowed."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed_categories = current_app.config.get('ALLOWED_EXTENSIONS', {})
    
    if category == 'all':
        all_exts = set()
        for cats in allowed_categories.values():
            all_exts.update(cats)
        return ext in all_exts
    
    return ext in allowed_categories.get(category, set())


def save_uploaded_file(file_storage, subfolder: str, allowed_category: str = 'document') -> str:
    """
    Saves an uploaded file securely with a unique filename prefix.
    Returns relative path from static folder or None if invalid.
    """
    if not file_storage or file_storage.filename == '':
        return None
    
    if not allowed_file(file_storage.filename, allowed_category):
        return None

    clean_filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex[:8]}_{clean_filename}"
    
    target_dir = Path(current_app.config['UPLOAD_FOLDER']) / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = target_dir / unique_name
    file_storage.save(str(file_path))
    
    # Return path relative to uploads: 'subfolder/unique_name'
    return f"{subfolder}/{unique_name}"


def calculate_grade(marks: float, max_marks: float) -> str:
    """Calculates letter grade based on percentage."""
    if max_marks <= 0:
        return 'N/A'
    pct = (marks / max_marks) * 100
    if pct >= 90:
        return 'A+'
    elif pct >= 80:
        return 'A'
    elif pct >= 70:
        return 'B+'
    elif pct >= 60:
        return 'B'
    elif pct >= 50:
        return 'C'
    elif pct >= 40:
        return 'D'
    else:
        return 'F'


def send_notification(user_id: int, title: str, message: str, link: str = None) -> Notification:
    """Creates an in-app notification for a user."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        link=link,
        is_read=False
    )
    db.session.add(notif)
    return notif
