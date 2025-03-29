from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort
from flask_login import current_user
from models import Article, Category, Comment, SiteSettings
from forms import CommentForm, SearchForm
import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Get homepage settings
    layout = SiteSettings.get('home_layout', 'grid')
    articles_per_page = int(SiteSettings.get('articles_per_page', 10))
    
    # Get featured articles
    featured_articles = Article.get_all(status='published', limit=5)
    
    # Get latest articles
    latest_articles = Article.get_all(status='published', limit=articles_per_page)
    
    # Get categories for navigation
    categories = Category.get_all()
    
    # Pass Category model to template
    return render_template('index.html', 
                           featured_articles=featured_articles,
                           latest_articles=latest_articles,
                           categories=categories,
                           Category=Category,
                           Article=Article,
                           layout=layout)

@main.route('/article/<slug>')
def article(slug):
    article = Article.get_by_slug(slug)
    if not article or article.status != 'published':
        abort(404)
    
    # Get related articles (same category or tags)
    related_articles = []
    if article.category_id:
        related_articles = Article.get_all(
            status='published', 
            category_id=article.category_id, 
            limit=3
        )
    
    # Remove current article from related
    related_articles = [a for a in related_articles if a.id != article.id]
    
    # Add more related by tags if needed
    if len(related_articles) < 3 and article.tags:
        for tag in article.tags:
            tag_articles = Article.get_all(status='published', tag=tag, limit=3)
            for a in tag_articles:
                if a.id != article.id and a not in related_articles:
                    related_articles.append(a)
                    if len(related_articles) >= 3:
                        break
            if len(related_articles) >= 3:
                break
    
    # Get author
    from models import User
    author = User.get_by_id(article.author_id)
    
    # Get category
    category = Category.get_by_id(article.category_id)
    
    # Get comments
    comments_enabled = SiteSettings.get('comments_enabled', True)
    comments = []
    if comments_enabled:
        comments = Comment.get_by_article_id(article.id, approved_only=True)
    
    # Comment form
    comment_form = CommentForm()
    
    return render_template('article.html', 
                           article=article, 
                           author=author,
                           category=category,
                           related_articles=related_articles,
                           comments=comments,
                           comments_enabled=comments_enabled,
                           comment_form=comment_form,
                           Category=Category,
                           Article=Article)

@main.route('/article/<slug>/comment', methods=['POST'])
def post_comment(slug):
    article = Article.get_by_slug(slug)
    if not article or article.status != 'published':
        abort(404)
    
    # Check if comments are enabled
    comments_enabled = SiteSettings.get('comments_enabled', True)
    if not comments_enabled:
        flash('Comments are disabled for this article.', 'error')
        return redirect(url_for('main.article', slug=slug))
    
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            article_id=article.id,
            author_name=form.author_name.data,
            author_email=form.author_email.data,
            content=form.content.data,
            parent_id=form.parent_id.data if form.parent_id.data else None,
            # Auto-approve if moderation is disabled
            approved=not SiteSettings.get('comments_moderation', True)
        )
        comment.save()
        
        if SiteSettings.get('comments_moderation', True):
            flash('Your comment has been submitted and is pending approval.', 'success')
        else:
            flash('Your comment has been posted successfully.', 'success')
            
        return redirect(url_for('main.article', slug=slug))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'error')
    
    return redirect(url_for('main.article', slug=slug))

@main.route('/category/<slug>')
def category(slug):
    category = Category.get_by_slug(slug)
    if not category:
        abort(404)
    
    page = request.args.get('page', 1, type=int)
    articles_per_page = int(SiteSettings.get('articles_per_page', 10))
    
    # Get articles for this category
    articles = Article.get_all(
        status='published', 
        category_id=category.id,
        limit=articles_per_page,
        offset=(page-1) * articles_per_page
    )
    
    # Get total count for pagination
    total_articles = len(Article.get_all(status='published', category_id=category.id))
    total_pages = (total_articles + articles_per_page - 1) // articles_per_page
    
    return render_template('category.html', 
                           category=category,
                           articles=articles,
                           page=page,
                           total_pages=total_pages,
                           Category=Category,
                           Article=Article)

@main.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    articles_per_page = int(SiteSettings.get('articles_per_page', 10))
    
    # Search articles
    articles = Article.search(
        query=query,
        limit=articles_per_page,
        offset=(page-1) * articles_per_page
    )
    
    # For pagination, we need the total count
    total_articles = len(Article.search(query=query))
    total_pages = (total_articles + articles_per_page - 1) // articles_per_page
    
    # Create search form for the header
    search_form = SearchForm()
    search_form.query.data = query
    
    return render_template('search.html', 
                           query=query,
                           articles=articles,
                           page=page,
                           total_pages=total_pages,
                           search_form=search_form,
                           Category=Category,
                           Article=Article)

@main.route('/tag/<tag>')
def tag(tag):
    page = request.args.get('page', 1, type=int)
    articles_per_page = int(SiteSettings.get('articles_per_page', 10))
    
    # Get articles with this tag
    articles = Article.get_all(
        status='published', 
        tag=tag,
        limit=articles_per_page,
        offset=(page-1) * articles_per_page
    )
    
    # Get total count for pagination
    total_articles = len(Article.get_all(status='published', tag=tag))
    total_pages = (total_articles + articles_per_page - 1) // articles_per_page
    
    return render_template('tag.html', 
                           tag=tag,
                           articles=articles,
                           page=page,
                           total_pages=total_pages,
                           Category=Category,
                           Article=Article)

@main.context_processor
def inject_site_settings():
    """Inject site settings into all templates"""
    settings = SiteSettings.get_all()
    
    # Add search form to all templates
    search_form = SearchForm()
    
    # Add categories for navigation
    categories = Category.get_all()
    
    return dict(settings=settings, 
                search_form=search_form, 
                categories=categories,
                Category=Category,
                Article=Article)
