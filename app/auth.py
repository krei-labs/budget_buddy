from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import User
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.banned:
                flash('Your account is banned.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        name = request.form.get('name', '').strip()
        age_str = request.form.get('age', '').strip()
        birthday_str = request.form.get('birthday', '').strip()
        email = request.form.get('email', '').strip()

        # Validate required fields
        if not username or not password or not confirm_password or not name or not age_str or not birthday_str or not email:
            flash('All fields are required. Please fill in everything.', 'danger')
            return redirect(url_for('auth.register'))

        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        # Validate age
        try:
            age = int(age_str)
            if age <= 0:
                raise ValueError
        except ValueError:
            flash('Age must be a valid positive number.', 'danger')
            return redirect(url_for('auth.register'))

        # Validate birthday
        try:
            birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Birthday must be a valid date.', 'danger')
            return redirect(url_for('auth.register'))

        # Check for existing username or email
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        # Create and save user
        user = User(username=username, name=name, age=age, birthday=birthday, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))