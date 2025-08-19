from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os
from functools import wraps  # Add this import

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🔑 Import blueprints AFTER extensions are initialized and models loaded
    from app.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.user_routes import user_bp

    # 🔗 Register blueprints with proper prefixes
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

    return app

def role_required(role):
    """Decorator to restrict access to users with a specific role."""
    def decorator(f):
        @wraps(f)  # Use wraps from functools
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                return redirect(url_for('auth.login'))  # Redirect non-admins to login
            return f(*args, **kwargs)
        return decorated_function
    return decorator
