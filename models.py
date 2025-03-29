import datetime
import uuid
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory database for MVP
_users = []
_articles = []
_comments = []
_media = []
_categories = []
_site_settings = {}

class User(UserMixin):
    def __init__(self, id=None, username=None, email=None, password=None, role='author', created_at=None):
        self.id = id or len(_users) + 1
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.role = role  # 'admin', 'editor', 'author'
        self.created_at = created_at or datetime.datetime.now()
        self.last_login = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def save(self):
        existing_user = User.get_by_email(self.email)
        if existing_user and existing_user.id != self.id:
            return False
        
        # Update existing user
        for i, user in enumerate(_users):
            if user.id == self.id:
                _users[i] = self
                return True
        
        # Add new user
        _users.append(self)
        return True
    
    @staticmethod
    def get_by_id(id):
        for user in _users:
            if user.id == id:
                return user
        return None
    
    @staticmethod
    def get_by_email(email):
        for user in _users:
            if user.email == email:
                return user
        return None
    
    @staticmethod
    def get_all():
        return _users

class Article:
    def __init__(self, id=None, title=None, content=None, author_id=None, category_id=None, 
                 status='draft', featured_image=None, tags=None, created_at=None, updated_at=None,
                 published_at=None, meta_title=None, meta_description=None, slug=None):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.author_id = author_id
        self.category_id = category_id
        self.status = status  # 'draft', 'scheduled', 'published', 'archived'
        self.featured_image = featured_image
        self.tags = tags or []
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = updated_at or datetime.datetime.now()
        self.published_at = published_at
        self.meta_title = meta_title or title
        self.meta_description = meta_description
        self.slug = slug or self._generate_slug()
        self.versions = []  # For version control
    
    def _generate_slug(self):
        if not self.title:
            return str(uuid.uuid4())
        # Convert title to slug format
        slug = self.title.lower()
        # Replace spaces with hyphens and remove special characters
        slug = ''.join(c if c.isalnum() else '-' for c in slug)
        # Remove duplicate hyphens
        while '--' in slug:
            slug = slug.replace('--', '-')
        # Trim hyphens from ends
        slug = slug.strip('-')
        return slug
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'category_id': self.category_id,
            'status': self.status,
            'featured_image': self.featured_image,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'slug': self.slug
        }
    
    def save(self):
        # Save previous version for version control
        if self.id:
            old_article = Article.get_by_id(self.id)
            if old_article:
                self.versions = old_article.versions.copy()
                self.versions.append({
                    'version': len(self.versions) + 1,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'content': old_article.content,
                    'title': old_article.title
                })
        
        self.updated_at = datetime.datetime.now()
        
        # Update existing article
        for i, article in enumerate(_articles):
            if article.id == self.id:
                _articles[i] = self
                return True
        
        # Add new article
        _articles.append(self)
        return True
    
    def publish(self, schedule_time=None):
        if schedule_time and schedule_time > datetime.datetime.now():
            self.status = 'scheduled'
            self.published_at = schedule_time
        else:
            self.status = 'published'
            self.published_at = datetime.datetime.now()
        self.save()
    
    def archive(self):
        self.status = 'archived'
        self.save()
    
    @staticmethod
    def get_by_id(id):
        for article in _articles:
            if article.id == id:
                return article
        return None
    
    @staticmethod
    def get_by_slug(slug):
        for article in _articles:
            if article.slug == slug:
                return article
        return None
    
    @staticmethod
    def get_all(status=None, category_id=None, author_id=None, tag=None, limit=None, offset=0):
        results = _articles.copy()
        
        # Filter by status
        if status:
            results = [a for a in results if a.status == status]
        
        # Filter by category
        if category_id:
            results = [a for a in results if a.category_id == category_id]
        
        # Filter by author
        if author_id:
            results = [a for a in results if a.author_id == author_id]
        
        # Filter by tag
        if tag:
            results = [a for a in results if tag in a.tags]
        
        # Sort by published date (newest first)
        results.sort(key=lambda x: x.published_at if x.published_at else x.created_at, reverse=True)
        
        # Apply pagination
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]
        
        return results
    
    @staticmethod
    def search(query, status='published', limit=None, offset=0):
        query = query.lower()
        results = []
        
        for article in _articles:
            if status and article.status != status:
                continue
                
            # Search in title, content, and tags
            if (query in article.title.lower() or 
                query in article.content.lower() or 
                any(query in tag.lower() for tag in article.tags)):
                results.append(article)
        
        # Sort by relevance (title match first, then content)
        results.sort(key=lambda x: (
            0 if query in x.title.lower() else 1,
            0 if query in x.content.lower() else 1,
            -(x.published_at.timestamp() if x.published_at else x.created_at.timestamp())
        ))
        
        # Apply pagination
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]
        
        return results

class Comment:
    def __init__(self, id=None, article_id=None, author_name=None, author_email=None, 
                 content=None, created_at=None, approved=False, parent_id=None):
        self.id = id or str(uuid.uuid4())
        self.article_id = article_id
        self.author_name = author_name
        self.author_email = author_email
        self.content = content
        self.created_at = created_at or datetime.datetime.now()
        self.approved = approved
        self.parent_id = parent_id  # For threaded comments
    
    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'approved': self.approved,
            'parent_id': self.parent_id
        }
    
    def save(self):
        # Update existing comment
        for i, comment in enumerate(_comments):
            if comment.id == self.id:
                _comments[i] = self
                return True
        
        # Add new comment
        _comments.append(self)
        return True
    
    def approve(self):
        self.approved = True
        self.save()
    
    @staticmethod
    def get_by_id(id):
        for comment in _comments:
            if comment.id == id:
                return comment
        return None
    
    @staticmethod
    def get_by_article_id(article_id, approved_only=True, limit=None, offset=0):
        results = [c for c in _comments if c.article_id == article_id]
        
        if approved_only:
            results = [c for c in results if c.approved]
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]
        
        return results
    
    @staticmethod
    def get_all(approved_only=False, limit=None, offset=0):
        results = _comments.copy()
        
        if approved_only:
            results = [c for c in results if c.approved]
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]
        
        return results

class Media:
    def __init__(self, id=None, filename=None, url=None, mime_type=None, 
                 size=None, uploaded_by=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.filename = filename
        self.url = url
        self.mime_type = mime_type
        self.size = size  # in bytes
        self.uploaded_by = uploaded_by  # user ID
        self.created_at = created_at or datetime.datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'url': self.url,
            'mime_type': self.mime_type,
            'size': self.size,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat()
        }
    
    def save(self):
        # Update existing media
        for i, media in enumerate(_media):
            if media.id == self.id:
                _media[i] = self
                return True
        
        # Add new media
        _media.append(self)
        return True
    
    @staticmethod
    def get_by_id(id):
        for media in _media:
            if media.id == id:
                return media
        return None
    
    @staticmethod
    def get_all(limit=None, offset=0):
        results = _media.copy()
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]
        
        return results

class Category:
    def __init__(self, id=None, name=None, slug=None, description=None, parent_id=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.slug = slug or self._generate_slug()
        self.description = description
        self.parent_id = parent_id  # For hierarchical categories
        self.created_at = created_at or datetime.datetime.now()
    
    def _generate_slug(self):
        if not self.name:
            return str(uuid.uuid4())
        # Convert name to slug format
        slug = self.name.lower()
        # Replace spaces with hyphens and remove special characters
        slug = ''.join(c if c.isalnum() else '-' for c in slug)
        # Remove duplicate hyphens
        while '--' in slug:
            slug = slug.replace('--', '-')
        # Trim hyphens from ends
        slug = slug.strip('-')
        return slug
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat()
        }
    
    def save(self):
        # Update existing category
        for i, category in enumerate(_categories):
            if category.id == self.id:
                _categories[i] = self
                return True
        
        # Add new category
        _categories.append(self)
        return True
    
    @staticmethod
    def get_by_id(id):
        for category in _categories:
            if category.id == id:
                return category
        return None
    
    @staticmethod
    def get_by_slug(slug):
        for category in _categories:
            if category.slug == slug:
                return category
        return None
    
    @staticmethod
    def get_all(parent_id=None):
        if parent_id:
            return [c for c in _categories if c.parent_id == parent_id]
        return _categories

class SiteSettings:
    @staticmethod
    def get(key, default=None):
        return _site_settings.get(key, default)
    
    @staticmethod
    def set(key, value):
        _site_settings[key] = value
        return True
    
    @staticmethod
    def get_all():
        return _site_settings.copy()
    
    @staticmethod
    def load_defaults():
        defaults = {
            'site_name': 'NewsPublisher',
            'site_description': 'Your source for the latest news and information',
            'contact_email': 'contact@example.com',
            'logo_url': '/static/images/logo.svg',
            'favicon_url': '/static/images/favicon.ico',
            'primary_color': '#1a1a1a',
            'secondary_color': '#f7f7f7',
            'accent_color': '#d32f2f',
            'text_color': '#2c2c2c',
            'link_color': '#0066cc',
            'home_layout': 'grid',  # 'grid', 'list', 'magazine'
            'articles_per_page': 10,
            'comments_enabled': True,
            'comments_moderation': True,
            'social_links': {
                'facebook': '',
                'twitter': '',
                'instagram': '',
                'linkedin': ''
            },
            'analytics_code': '',
            'header_scripts': '',
            'footer_scripts': '',
            'custom_css': ''
        }
        
        for key, value in defaults.items():
            if key not in _site_settings:
                _site_settings[key] = value
