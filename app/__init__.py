import os
from pathlib import Path

from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

from config import config_by_name
from app.models import db, User, Notification, Department

login_manager = LoginManager()
csrf = CSRFProtect()


def initialize_database(app: Flask) -> None:
    """
    Create any missing tables and add the standard departments when the
    departments table is empty. This is safe to run on application startup:
    it does not drop tables or delete existing records.
    """
    with app.app_context():
        db.create_all()

        # The registration page expects departments to exist. Add defaults
        # only when there are no departments, preserving any existing data.
        if Department.query.count() == 0:
            db.session.add_all([
                Department(
                    code='CSE',
                    name='Computer Science & Engineering',
                    description='Department of Computer Science and Software Engineering.',
                ),
                Department(
                    code='IT',
                    name='Information Technology',
                    description='Department of Information Technology and Cloud Systems.',
                ),
                Department(
                    code='ECE',
                    name='Electronics & Communication',
                    description='Department of Electronics and Signal Processing.',
                ),
                Department(
                    code='ME',
                    name='Mechanical Engineering',
                    description='Department of Mechanical and Industrial Systems.',
                ),
            ])
            db.session.commit()


def create_app(config_name: str = None) -> Flask:
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        if config_name not in config_by_name:
            config_name = 'development'

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Ensure required directories exist.
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    for sub in ['avatars', 'assignments', 'submissions', 'materials']:
        (upload_folder / sub).mkdir(parents=True, exist_ok=True)

    # Initialize extensions.
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to access StudentHub.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Import and register blueprints. Importing the models module above
    # registers all model classes with SQLAlchemy's metadata.
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Initialize the schema in both local execution and Gunicorn/Render.
    # Unlike code under `if __name__ == "__main__"` in run.py, this runs
    # when Gunicorn imports `run:app`.
    initialize_database(app)

    # Root redirect.
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('auth.login'))

    # Context processors.
    @app.context_processor
    def inject_global_data():
        unread_count = 0
        latest_notifications = []
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False,
            ).count()
            latest_notifications = (
                Notification.query.filter_by(user_id=current_user.id)
                .order_by(Notification.created_at.desc())
                .limit(5)
                .all()
            )

        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': latest_notifications,
            'app_name': 'StudentHub',
        }

    # Custom Jinja template filters.
    @app.template_filter('format_datetime')
    def format_datetime(value, format='%b %d, %Y %I:%M %p'):
        if value is None:
            return ''
        return value.strftime(format)

    @app.template_filter('format_date')
    def format_date(value, format='%b %d, %Y'):
        if value is None:
            return ''
        return value.strftime(format)

    @app.template_filter('format_time')
    def format_time(value, format='%I:%M %p'):
        if value is None:
            return ''
        return value.strftime(format)

    # Error handlers.
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
