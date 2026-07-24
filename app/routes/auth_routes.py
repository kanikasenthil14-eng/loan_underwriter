from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import mongo, bcrypt
from app.models.user_model import UserModel
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard') if current_user.is_admin() else url_for('customer.dashboard'))
    return render_template('auth/landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user_data = mongo.db.users.find_one({'email': email})
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = UserModel(user_data)
            login_user(user, remember=request.form.get('remember') == 'on')
            return redirect(url_for('admin.dashboard') if user.is_admin() else url_for('customer.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not all([name, email, mobile, password]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        mongo.db.users.insert_one({
            'name': name, 'email': email, 'mobile': mobile,
            'password': hashed, 'role': 'customer',
            'created_at': datetime.utcnow()
        })
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
