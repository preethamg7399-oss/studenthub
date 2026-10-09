import os
from app import create_app, db

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Ensure database tables exist if running directly
    with app.app_context():
        db.create_all()

    port = int(os.environ.get('PORT', 5000))
    debug = env == 'development'
    print(f"\n=======================================================")
    print(f"  Starting StudentHub Portal on http://127.0.0.1:{port} ")
    print(f"  Environment: {env} (Debug={debug})")
    print(f"=======================================================\n")
    app.run(host='127.0.0.1', port=port, debug=debug)
