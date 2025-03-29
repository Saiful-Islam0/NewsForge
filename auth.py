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
    
    # Import required data for template
    from models import SiteSettings, Category, Article
    from forms import SearchForm
    
    settings = SiteSettings.get_all()
    search_form = SearchForm()
    categories = Category.get_all()
    
    return render_template('auth/login.html', 
                          form=form,
                          settings=settings,
                          Category=Category,
                          Article=Article,
                          search_form=search_form,
                          categories=categories)

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
            
            # Import required data for template
            from models import SiteSettings, Category, Article
            from forms import SearchForm
            
            settings = SiteSettings.get_all()
            search_form = SearchForm()
            categories = Category.get_all()
            
            return render_template('auth/register.html', 
                                  form=form,
                                  settings=settings,
                                  Category=Category,
                                  Article=Article,
                                  search_form=search_form,
                                  categories=categories)
        
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
    
    # Import required data for template
    from models import SiteSettings, Category, Article
    from forms import SearchForm
    
    settings = SiteSettings.get_all()
    search_form = SearchForm()
    categories = Category.get_all()
    
    return render_template('auth/register.html', 
                          form=form,
                          settings=settings,
                          Category=Category,
                          Article=Article,
                          search_form=search_form,
                          categories=categories)

@auth.route('/profile')
@login_required
def profile():
    """User profile page for public portal users"""
    # Import required data for template
    from models import SiteSettings, Category, Article, Comment
    from forms import SearchForm
    
    settings = SiteSettings.get_all()
    search_form = SearchForm()
    categories = Category.get_all()
    
    # Get user's comments if any
    user_comments = []
    if current_user.is_authenticated:
        # This would ideally retrieve the user's comments
        # For now, we'll leave it as a placeholder
        pass
    
    return render_template('auth/profile.html', 
                          settings=settings,
                          Category=Category,
                          Article=Article,
                          search_form=search_form,
                          categories=categories,
                          user_comments=user_comments)
