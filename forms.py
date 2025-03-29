from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, BooleanField, DateTimeField, FileField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL
from flask_wtf.file import FileAllowed
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=str, validators=[DataRequired()])
    tags = StringField('Tags (comma separated)', validators=[Optional()])
    featured_image = FileField('Featured Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'svg'], 'Images only!')
    ])
    featured_image_url = StringField('Featured Image URL', validators=[Optional(), URL()])
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], validators=[DataRequired()])
    publish_date = DateTimeField('Publish Date', format='%Y-%m-%d %H:%M', validators=[Optional()])
    meta_title = StringField('Meta Title', validators=[Optional(), Length(max=200)])
    meta_description = TextAreaField('Meta Description', validators=[Optional(), Length(max=200)])
    slug = StringField('Slug', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save')

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    slug = StringField('Slug', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    parent_id = SelectField('Parent Category', coerce=str, validators=[Optional()])
    submit = SubmitField('Save')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('author', 'Author')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        Optional(), EqualTo('password')
    ])
    submit = SubmitField('Save')

class CommentForm(FlaskForm):
    author_name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    author_email = StringField('Email', validators=[DataRequired(), Email()])
    content = TextAreaField('Comment', validators=[DataRequired()])
    parent_id = HiddenField('Parent Comment ID')
    submit = SubmitField('Post Comment')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class MediaUploadForm(FlaskForm):
    file = FileField('File', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'svg'], 'Images only!')
    ])
    submit = SubmitField('Upload')

class SiteSettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(max=100)])
    site_description = TextAreaField('Site Description', validators=[Optional()])
    contact_email = StringField('Contact Email', validators=[Optional(), Email()])
    logo_url = StringField('Logo URL', validators=[Optional(), URL()])
    favicon_url = StringField('Favicon URL', validators=[Optional(), URL()])
    primary_color = StringField('Primary Color', validators=[Optional()])
    secondary_color = StringField('Secondary Color', validators=[Optional()])
    accent_color = StringField('Accent Color', validators=[Optional()])
    text_color = StringField('Text Color', validators=[Optional()])
    link_color = StringField('Link Color', validators=[Optional()])
    home_layout = SelectField('Home Layout', choices=[
        ('grid', 'Grid'),
        ('list', 'List'),
        ('magazine', 'Magazine')
    ], validators=[Optional()])
    articles_per_page = StringField('Articles Per Page', validators=[Optional()])
    comments_enabled = BooleanField('Enable Comments')
    comments_moderation = BooleanField('Moderate Comments')
    facebook_url = StringField('Facebook URL', validators=[Optional(), URL()])
    twitter_url = StringField('Twitter URL', validators=[Optional(), URL()])
    instagram_url = StringField('Instagram URL', validators=[Optional(), URL()])
    linkedin_url = StringField('LinkedIn URL', validators=[Optional(), URL()])
    analytics_code = TextAreaField('Analytics Code', validators=[Optional()])
    header_scripts = TextAreaField('Header Scripts', validators=[Optional()])
    footer_scripts = TextAreaField('Footer Scripts', validators=[Optional()])
    custom_css = TextAreaField('Custom CSS', validators=[Optional()])
    submit = SubmitField('Save Settings')
