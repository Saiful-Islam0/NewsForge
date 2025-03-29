import os

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'default-dev-secret-key')
    DEBUG = True
    
    # Application Settings
    SITE_NAME = "NewsPublisher"
    SITE_DESCRIPTION = "Your source for the latest news and information"
    ADMIN_EMAIL = "admin@example.com"
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB maximum file size
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    
    # Pagination Settings
    ARTICLES_PER_PAGE = 10
    COMMENTS_PER_PAGE = 20
    
    # Theme Settings (Default)
    PRIMARY_COLOR = "#1a1a1a"
    SECONDARY_COLOR = "#f7f7f7"
    ACCENT_COLOR = "#d32f2f"
    TEXT_COLOR = "#2c2c2c"
    LINK_COLOR = "#0066cc"
