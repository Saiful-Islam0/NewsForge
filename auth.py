from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            
            # Update last login time
            import datetime
            user.last_login = datetime.datetime.now()
            user.save()
            
            # Redirect to requested page or default
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect based on role
            if user.role == 'admin' or user.role == 'editor':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if email already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Email is already registered.', 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user (default role is author)
        user = User(
            username=username,
            email=email,
            password=password,
            role='author'
        )
        user.save()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/profile')
@login_required
def profile():
    return redirect(url_for('admin.profile'))
