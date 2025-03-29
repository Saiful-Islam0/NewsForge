from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user, login_user, logout_user
from models import User, Article, Category, Comment, Media, SiteSettings
from forms import ArticleForm, CategoryForm, UserForm, SiteSettingsForm, MediaUploadForm, LoginForm
import datetime
import os
import uuid
from werkzeug.utils import secure_filename

admin = Blueprint('admin', __name__)

# Admin middleware
@admin.before_request
def check_admin():
    # Allow access to login route without authentication
    if request.endpoint == 'admin.login':
        return None
        
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login', next=request.url))
    
    # Only admin and editor roles can access admin panel
    if current_user.role not in ['admin', 'editor']:
        flash('You do not have permission to access the admin panel.', 'error')
        return redirect(url_for('main.index'))

@admin.route('/')
@login_required
def dashboard():
    # Get counts for dashboard
    article_count = len(Article.get_all())
    published_count = len(Article.get_all(status='published'))
    draft_count = len(Article.get_all(status='draft'))
    
    # Get latest articles
    latest_articles = Article.get_all(limit=5)
    
    # Get pending comments if admin/editor
    pending_comments = []
    if current_user.role in ['admin', 'editor']:
        pending_comments = [c for c in Comment.get_all() if not c.approved]
    
    return render_template('admin/dashboard.html',
                           article_count=article_count,
                           published_count=published_count,
                           draft_count=draft_count,
                           latest_articles=latest_articles,
                           pending_comments=pending_comments)

@admin.route('/articles')
@login_required
def articles():
    status = request.args.get('status', '')
    
    # Get articles based on user role
    if current_user.role == 'admin' or current_user.role == 'editor':
        articles = Article.get_all(status=status if status else None)
    else:
        articles = Article.get_all(status=status if status else None, author_id=current_user.id)
    
    return render_template('admin/articles.html', articles=articles, current_status=status)

@admin.route('/articles/new', methods=['GET', 'POST'])
@login_required
def new_article():
    form = ArticleForm()
    
    # Populate category choices
    categories = Category.get_all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        # Process tags
        tags = []
        if form.tags.data:
            tags = [tag.strip() for tag in form.tags.data.split(',')]
        
        # Handle featured image
        featured_image = None
        if form.featured_image.data:
            filename = secure_filename(form.featured_image.data.filename)
            # Create unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
            
            # Create directory if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_folder, unique_filename)
            form.featured_image.data.save(file_path)
            
            # Set the URL
            featured_image = f"/{current_app.config['UPLOAD_FOLDER']}/{unique_filename}"
        elif form.featured_image_url.data:
            featured_image = form.featured_image_url.data
        
        # Create article
        article = Article(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            category_id=form.category_id.data,
            status=form.status.data,
            featured_image=featured_image,
            tags=tags,
            meta_title=form.meta_title.data,
            meta_description=form.meta_description.data,
            slug=form.slug.data if form.slug.data else None
        )
        
        # Handle publishing
        if form.status.data == 'published':
            article.published_at = datetime.datetime.now()
        elif form.status.data == 'scheduled' and form.publish_date.data:
            article.published_at = form.publish_date.data
            
        article.save()
        
        flash('Article created successfully!', 'success')
        return redirect(url_for('admin.articles'))
    
    return render_template('admin/edit_article.html', form=form, article=None)

@admin.route('/articles/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = Article.get_by_id(id)
    if not article:
        abort(404)
    
    # Check permissions
    if current_user.role == 'author' and article.author_id != current_user.id:
        flash('You do not have permission to edit this article.', 'error')
        return redirect(url_for('admin.articles'))
    
    form = ArticleForm(obj=article)
    
    # Populate category choices
    categories = Category.get_all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    # Set initial values
    if request.method == 'GET':
        form.tags.data = ', '.join(article.tags) if article.tags else ''
        if article.published_at:
            form.publish_date.data = article.published_at
    
    if form.validate_on_submit():
        # Process tags
        tags = []
        if form.tags.data:
            tags = [tag.strip() for tag in form.tags.data.split(',')]
        
        # Handle featured image
        featured_image = article.featured_image
        if form.featured_image.data:
            filename = secure_filename(form.featured_image.data.filename)
            # Create unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
            
            # Create directory if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_folder, unique_filename)
            form.featured_image.data.save(file_path)
            
            # Set the URL
            featured_image = f"/{current_app.config['UPLOAD_FOLDER']}/{unique_filename}"
        elif form.featured_image_url.data:
            featured_image = form.featured_image_url.data
        
        # Update article
        article.title = form.title.data
        article.content = form.content.data
        article.category_id = form.category_id.data
        article.status = form.status.data
        article.featured_image = featured_image
        article.tags = tags
        article.meta_title = form.meta_title.data
        article.meta_description = form.meta_description.data
        article.slug = form.slug.data if form.slug.data else article._generate_slug()
        
        # Handle publishing
        if form.status.data == 'published' and article.status != 'published':
            article.published_at = datetime.datetime.now()
        elif form.status.data == 'scheduled' and form.publish_date.data:
            article.published_at = form.publish_date.data
            
        article.save()
        
        flash('Article updated successfully!', 'success')
        return redirect(url_for('admin.articles'))
    
    return render_template('admin/edit_article.html', form=form, article=article)

@admin.route('/articles/delete/<id>', methods=['POST'])
@login_required
def delete_article(id):
    article = Article.get_by_id(id)
    if not article:
        abort(404)
    
    # Check permissions
    if current_user.role == 'author' and article.author_id != current_user.id:
        flash('You do not have permission to delete this article.', 'error')
        return redirect(url_for('admin.articles'))
    
    # Remove article from list
    global _articles
    _articles = [a for a in _articles if a.id != article.id]
    
    flash('Article deleted successfully!', 'success')
    return redirect(url_for('admin.articles'))

@admin.route('/categories')
@login_required
def categories():
    # Only admin and editor can manage categories
    if current_user.role not in ['admin', 'editor']:
        flash('You do not have permission to manage categories.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    categories = Category.get_all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    # Only admin and editor can manage categories
    if current_user.role not in ['admin', 'editor']:
        flash('You do not have permission to manage categories.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = CategoryForm()
    
    # Populate parent category choices
    categories = Category.get_all()
    form.parent_id.choices = [('', 'None')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            slug=form.slug.data if form.slug.data else None,
            description=form.description.data,
            parent_id=form.parent_id.data if form.parent_id.data else None
        )
        category.save()
        
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/edit_category.html', form=form, category=None)

@admin.route('/categories/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    # Only admin and editor can manage categories
    if current_user.role not in ['admin', 'editor']:
        flash('You do not have permission to manage categories.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    category = Category.get_by_id(id)
    if not category:
        abort(404)
    
    form = CategoryForm(obj=category)
    
    # Populate parent category choices (excluding self to prevent circular references)
    categories = [c for c in Category.get_all() if c.id != category.id]
    form.parent_id.choices = [('', 'None')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.slug = form.slug.data if form.slug.data else category._generate_slug()
        category.description = form.description.data
        category.parent_id = form.parent_id.data if form.parent_id.data else None
        category.save()
        
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/edit_category.html', form=form, category=category)

@admin.route('/categories/delete/<id>', methods=['POST'])
@login_required
def delete_category(id):
    # Only admin and editor can manage categories
    if current_user.role not in ['admin', 'editor']:
        flash('You do not have permission to manage categories.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    category = Category.get_by_id(id)
    if not category:
        abort(404)
    
    # Check if category has articles
    articles = Article.get_all(category_id=category.id)
    if articles:
        flash('Cannot delete category with associated articles.', 'error')
        return redirect(url_for('admin.categories'))
    
    # Check if category has subcategories
    subcategories = Category.get_all(parent_id=category.id)
    if subcategories:
        flash('Cannot delete category with subcategories.', 'error')
        return redirect(url_for('admin.categories'))
    
    # Remove category from list
    global _categories
    _categories = [c for c in _categories if c.id != category.id]
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin.categories'))

@admin.route('/comments')
@login_required
def comments():
    # Only admin and editor can manage all comments
    if current_user.role not in ['admin', 'editor']:
        flash('You do not have permission to manage comments.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    status = request.args.get('status', '')
    
    if status == 'pending':
        comments = [c for c in Comment.get_all() if not c.approved]
    elif status == 'approved':
        comments = [c for c in Comment.get_all() if c.approved]
    else:
        comments = Comment.get_all()
    
    # Get articles for displaying titles
    articles = {a.id: a for a in Article.get_all()}
    
    return render_template('admin/comments.html', 
                           comments=comments, 
                           articles=articles,
                           current_status=status)

@admin.route('/comments/approve/<id>', methods=['POST'])
@login_required
def approve_comment(id):
    # Only admin and editor can manage comments
    if current_user.role not in ['admin', 'editor']:
        flash('You do not have permission to manage comments.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    comment = Comment.get_by_id(id)
    if not comment:
        abort(404)
    
    comment.approved = True
    comment.save()
    
    flash('Comment approved successfully!', 'success')
    return redirect(url_for('admin.comments'))

@admin.route('/comments/delete/<id>', methods=['POST'])
@login_required
def delete_comment(id):
    # Only admin and editor can manage comments
    if current_user.role not in ['admin', 'editor']:
        flash('You do not have permission to manage comments.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    comment = Comment.get_by_id(id)
    if not comment:
        abort(404)
    
    # Remove comment from list
    global _comments
    _comments = [c for c in _comments if c.id != comment.id]
    
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('admin.comments'))

@admin.route('/media')
@login_required
def media():
    media_files = Media.get_all()
    form = MediaUploadForm()
    return render_template('admin/media.html', media_files=media_files, form=form)

@admin.route('/media/upload', methods=['POST'])
@login_required
def upload_media():
    form = MediaUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        
        # Create unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
        
        # Create directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create media entry
        media = Media(
            filename=filename,
            url=f"/{current_app.config['UPLOAD_FOLDER']}/{unique_filename}",
            mime_type=file.content_type,
            size=file_size,
            uploaded_by=current_user.id
        )
        media.save()
        
        flash('File uploaded successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')
    
    return redirect(url_for('admin.media'))

@admin.route('/media/delete/<id>', methods=['POST'])
@login_required
def delete_media(id):
    media_file = Media.get_by_id(id)
    if not media_file:
        abort(404)
    
    # Remove file from filesystem if it exists
    file_path = os.path.join(current_app.root_path, media_file.url.lstrip('/'))
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove media from list
    global _media
    _media = [m for m in _media if m.id != media_file.id]
    
    flash('File deleted successfully!', 'success')
    return redirect(url_for('admin.media'))

@admin.route('/users')
@login_required
def users():
    # Only admin can manage users
    if current_user.role != 'admin':
        flash('You do not have permission to manage users.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    # Only admin can manage users
    if current_user.role != 'admin':
        flash('You do not have permission to manage users.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = UserForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.get_by_email(form.email.data)
        if existing_user:
            flash('Email is already registered.', 'error')
            return render_template('admin/edit_user.html', form=form, user=None)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role=form.role.data
        )
        user.save()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', form=form, user=None)

@admin.route('/users/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    # Only admin can edit other users
    if current_user.role != 'admin' and str(current_user.id) != id:
        flash('You do not have permission to edit this user.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    user = User.get_by_id(int(id))
    if not user:
        abort(404)
    
    form = UserForm(obj=user)
    
    # If not admin, remove role field
    if current_user.role != 'admin':
        del form.role
    
    if form.validate_on_submit():
        # Check if email already exists for another user
        existing_user = User.get_by_email(form.email.data)
        if existing_user and existing_user.id != user.id:
            flash('Email is already registered by another user.', 'error')
            return render_template('admin/edit_user.html', form=form, user=user)
        
        # Update user
        user.username = form.username.data
        user.email = form.email.data
        
        # Update role if admin
        if current_user.role == 'admin':
            user.role = form.role.data
        
        # Update password if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        user.save()
        
        flash('User updated successfully!', 'success')
        
        # Redirect based on user role
        if current_user.role == 'admin':
            return redirect(url_for('admin.users'))
        else:
            return redirect(url_for('admin.profile'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin.route('/users/delete/<id>', methods=['POST'])
@login_required
def delete_user(id):
    # Only admin can delete users
    if current_user.role != 'admin':
        flash('You do not have permission to delete users.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    user = User.get_by_id(int(id))
    if not user:
        abort(404)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    # Remove user from list
    global _users
    _users = [u for u in _users if u.id != user.id]
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page - separate from public user login"""
    if current_user.is_authenticated and current_user.role in ['admin', 'editor']:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password) and user.role in ['admin', 'editor']:
            login_user(user, remember=remember)
            
            # Update last login time if the attribute exists
            if hasattr(user, 'last_login'):
                user.last_login = datetime.datetime.now()
                user.save()
            
            # Redirect to admin dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/admin'):
                return redirect(next_page)
                
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password, or you do not have admin privileges.', 'error')
    
    # Get site settings to pass to the template
    settings = SiteSettings.get_all()
    return render_template('admin/login.html', form=form, settings=settings)

@admin.route('/logout')
@login_required
def logout():
    """Admin logout - redirects to admin login page"""
    logout_user()
    flash('You have been logged out from the admin panel.', 'success')
    return redirect(url_for('admin.login'))

@admin.route('/profile')
@login_required
def profile():
    return redirect(url_for('admin.edit_user', id=current_user.id))

@admin.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Only admin can manage site settings
    if current_user.role != 'admin':
        flash('You do not have permission to manage site settings.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = SiteSettingsForm()
    
    # Populate form with current settings
    if request.method == 'GET':
        settings = SiteSettings.get_all()
        form.site_name.data = settings.get('site_name', 'NewsPublisher')
        form.site_description.data = settings.get('site_description', '')
        form.contact_email.data = settings.get('contact_email', '')
        form.logo_url.data = settings.get('logo_url', '')
        form.favicon_url.data = settings.get('favicon_url', '')
        form.primary_color.data = settings.get('primary_color', '#1a1a1a')
        form.secondary_color.data = settings.get('secondary_color', '#f7f7f7')
        form.accent_color.data = settings.get('accent_color', '#d32f2f')
        form.text_color.data = settings.get('text_color', '#2c2c2c')
        form.link_color.data = settings.get('link_color', '#0066cc')
        form.home_layout.data = settings.get('home_layout', 'grid')
        form.articles_per_page.data = str(settings.get('articles_per_page', 10))
        form.comments_enabled.data = settings.get('comments_enabled', True)
        form.comments_moderation.data = settings.get('comments_moderation', True)
        form.facebook_url.data = settings.get('social_links', {}).get('facebook', '')
        form.twitter_url.data = settings.get('social_links', {}).get('twitter', '')
        form.instagram_url.data = settings.get('social_links', {}).get('instagram', '')
        form.linkedin_url.data = settings.get('social_links', {}).get('linkedin', '')
        form.analytics_code.data = settings.get('analytics_code', '')
        form.header_scripts.data = settings.get('header_scripts', '')
        form.footer_scripts.data = settings.get('footer_scripts', '')
        form.custom_css.data = settings.get('custom_css', '')
    
    if form.validate_on_submit():
        # Update settings
        SiteSettings.set('site_name', form.site_name.data)
        SiteSettings.set('site_description', form.site_description.data)
        SiteSettings.set('contact_email', form.contact_email.data)
        SiteSettings.set('logo_url', form.logo_url.data)
        SiteSettings.set('favicon_url', form.favicon_url.data)
        SiteSettings.set('primary_color', form.primary_color.data)
        SiteSettings.set('secondary_color', form.secondary_color.data)
        SiteSettings.set('accent_color', form.accent_color.data)
        SiteSettings.set('text_color', form.text_color.data)
        SiteSettings.set('link_color', form.link_color.data)
        SiteSettings.set('home_layout', form.home_layout.data)
        
        try:
            articles_per_page = int(form.articles_per_page.data)
            SiteSettings.set('articles_per_page', articles_per_page)
        except:
            SiteSettings.set('articles_per_page', 10)
        
        SiteSettings.set('comments_enabled', form.comments_enabled.data)
        SiteSettings.set('comments_moderation', form.comments_moderation.data)
        
        # Social links
        social_links = {
            'facebook': form.facebook_url.data,
            'twitter': form.twitter_url.data,
            'instagram': form.instagram_url.data,
            'linkedin': form.linkedin_url.data
        }
        SiteSettings.set('social_links', social_links)
        
        SiteSettings.set('analytics_code', form.analytics_code.data)
        SiteSettings.set('header_scripts', form.header_scripts.data)
        SiteSettings.set('footer_scripts', form.footer_scripts.data)
        SiteSettings.set('custom_css', form.custom_css.data)
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', form=form)
