import os
import logging
import datetime

from flask import Flask
from flask_login import LoginManager
import jinja2

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret-key")

# Enable Jinja2 extensions
app.jinja_env.add_extension('jinja2.ext.do')

# Add utility functions to Jinja2 templates
app.jinja_env.globals['now'] = datetime.datetime.now

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import routes after app initialization to avoid circular imports
from routes import main
from auth import auth
from admin import admin

# Register blueprints
app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Import at the end to avoid circular imports
from flask import render_template
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

# Initialize app data on startup
with app.app_context():
    from utils import init_db
    init_db()
