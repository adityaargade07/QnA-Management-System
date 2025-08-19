from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

# Register Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')  # Default role is 'user'

        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("User already exists.")
            return redirect(url_for('auth.register'))

        # Hash password
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Create new user and commit to DB
        new_user = User(username=username, email=email, password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registered successfully! You can now login.")
        return redirect(url_for('auth.login'))  # Redirect to login page

    return render_template('register.html')


# Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find user by username
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully.")
            
            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
    return render_template('login.html')


# Logout Route
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login'))  # Redirect to login page after logout
