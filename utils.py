import datetime
from models import User, Category, Article, SiteSettings
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize database with default data"""
    # Load default site settings
    SiteSettings.load_defaults()
    
    # Create default admin user if no users exist
    if not User.get_all():
        admin = User(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            role="admin"
        )
        admin.save()
    
    # Create default categories if none exist
    if not Category.get_all():
        categories = [
            {"name": "News", "description": "Latest news and updates"},
            {"name": "Technology", "description": "Technology news and reviews"},
            {"name": "Politics", "description": "Political news and analysis"},
            {"name": "Business", "description": "Business and finance news"},
            {"name": "Sports", "description": "Sports news and results"},
            {"name": "Entertainment", "description": "Entertainment news and reviews"},
            {"name": "Science", "description": "Science news and discoveries"}
        ]
        
        for cat in categories:
            category = Category(name=cat["name"], description=cat["description"])
            category.save()
    
    # Create sample article if none exist
    if not Article.get_all():
        first_category = Category.get_all()[0]
        admin_user = User.get_by_email("admin@example.com")
        
        welcome_article = Article(
            title="Welcome to NewsPublisher",
            content="""
<p>Welcome to your new news publishing platform! This is a sample article to help you get started. Feel free to edit or delete it.</p>

<h2>Features</h2>
<p>Here are some of the key features of your new platform:</p>
<ul>
    <li>Content Management System with role-based access</li>
    <li>Article lifecycle management (draft, schedule, publish, archive)</li>
    <li>Version control for articles</li>
    <li>Media library for images and other assets</li>
    <li>Public news portal with responsive design</li>
    <li>Commenting system with moderation options</li>
    <li>SEO optimization tools</li>
</ul>

<h2>Getting Started</h2>
<p>To get started, log in to the admin panel and:</p>
<ol>
    <li>Update your site settings</li>
    <li>Create or modify categories</li>
    <li>Create your first real article</li>
    <li>Customize your theme</li>
</ol>

<p>Enjoy your new publishing platform!</p>
            """,
            author_id=admin_user.id,
            category_id=first_category.id,
            status="published",
            tags=["welcome", "getting-started"],
            published_at=datetime.datetime.now()
        )
        welcome_article.save()

def generate_sitemap():
    """Generate XML sitemap for SEO"""
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Add homepage
    sitemap += '  <url>\n'
    sitemap += '    <loc>https://example.com/</loc>\n'
    sitemap += f'    <lastmod>{datetime.datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
    sitemap += '    <changefreq>daily</changefreq>\n'
    sitemap += '    <priority>1.0</priority>\n'
    sitemap += '  </url>\n'
    
    # Add categories
    for category in Category.get_all():
        sitemap += '  <url>\n'
        sitemap += f'    <loc>https://example.com/category/{category.slug}</loc>\n'
        sitemap += f'    <lastmod>{datetime.datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap += '    <changefreq>weekly</changefreq>\n'
        sitemap += '    <priority>0.8</priority>\n'
        sitemap += '  </url>\n'
    
    # Add published articles
    for article in Article.get_all(status='published'):
        sitemap += '  <url>\n'
        sitemap += f'    <loc>https://example.com/article/{article.slug}</loc>\n'
        sitemap += f'    <lastmod>{article.updated_at.strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap += '    <changefreq>monthly</changefreq>\n'
        sitemap += '    <priority>0.6</priority>\n'
        sitemap += '  </url>\n'
    
    sitemap += '</urlset>'
    return sitemap

def generate_rss():
    """Generate RSS feed for articles"""
    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += '<rss version="2.0">\n'
    rss += '  <channel>\n'
    rss += f'    <title>{SiteSettings.get("site_name", "NewsPublisher")}</title>\n'
    rss += f'    <link>https://example.com/</link>\n'
    rss += f'    <description>{SiteSettings.get("site_description", "")}</description>\n'
    rss += f'    <language>en-us</language>\n'
    rss += f'    <lastBuildDate>{datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>\n'
    
    # Add published articles
    for article in Article.get_all(status='published', limit=10):
        rss += '    <item>\n'
        rss += f'      <title>{article.title}</title>\n'
        rss += f'      <link>https://example.com/article/{article.slug}</link>\n'
        rss += f'      <description>{article.meta_description or article.title}</description>\n'
        rss += f'      <pubDate>{article.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>\n'
        rss += f'      <guid>https://example.com/article/{article.slug}</guid>\n'
        rss += '    </item>\n'
    
    rss += '  </channel>\n'
    rss += '</rss>'
    return rss

def format_date(date, format='%B %d, %Y'):
    """Format date for display"""
    if not date:
        return ""
    return date.strftime(format)

def truncate_text(text, length=100):
    """Truncate text for display"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'
