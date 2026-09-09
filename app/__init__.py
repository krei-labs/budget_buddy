from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from datetime import date  # Added import for date objects

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

from . import models

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-this'  # Change this to a secure key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_buddy.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAINTENANCE_MODE'] = False  # Flag for maintenance mode (toggled by admin)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'  # Redirect to login if not authenticated

    from .routes import main
    from .auth import auth  # New auth blueprint
    app.register_blueprint(main)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()
        # Create default admin user if no users exist
        from .models import User
        if not User.query.first():
            admin = User(username='admin', name='Admin User', age=30, birthday=date(1994, 1, 1), email='admin@budgetbuddy.com', role='admin')  # Fixed to use date object
            admin.set_password('admin123')  # Default password; change after login
            db.session.add(admin)
            db.session.commit()

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))