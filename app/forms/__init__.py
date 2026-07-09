from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField, SelectField,
                     BooleanField, EmailField, TelField, SubmitField, DateTimeLocalField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from flask_wtf.file import FileField, FileAllowed


# ─── AUTH ────────────────────────────────────────────────────────────────────
class RegistrationForm(FlaskForm):
    full_name   = StringField('Full Name', validators=[DataRequired(), Length(2, 120)])
    email       = EmailField('Email', validators=[DataRequired(), Email()])
    phone       = TelField('Phone', validators=[Optional(), Length(max=20)])
    city        = StringField('City', validators=[Optional(), Length(max=80)])
    state       = StringField('State', validators=[Optional(), Length(max=80)])
    password    = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_pw  = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit      = SubmitField('Create Account')

    def validate_password(self, field):
        pw = field.data
        if not any(c.isupper() for c in pw):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(c.isdigit() for c in pw):
            raise ValidationError('Password must contain at least one digit.')


class LoginForm(FlaskForm):
    email       = EmailField('Email', validators=[DataRequired(), Email()])
    password    = PasswordField('Password', validators=[DataRequired()])
    remember    = BooleanField('Remember me')
    submit      = SubmitField('Sign In')


# ─── MEMBERSHIP APPLICATION ──────────────────────────────────────────────────
MEMBERSHIP_TYPES = [
    ('Individual Advocate', 'Individual Advocate'),
    ('Caregiver',           'Caregiver'),
    ('Healthcare Professional', 'Healthcare Professional'),
    ('NGO / Foundation',    'NGO / Foundation'),
    ('Patient Group',       'Patient Group'),
    ('Corporate Partner',   'Corporate Partner'),
]

class MembershipForm(FlaskForm):
    full_name       = StringField('Full Name', validators=[DataRequired(), Length(2, 120)])
    email           = EmailField('Email', validators=[DataRequired(), Email()])
    phone           = TelField('Phone', validators=[Optional(), Length(max=20)])
    membership_type = SelectField('Membership Type', choices=MEMBERSHIP_TYPES, validators=[DataRequired()])
    organization    = StringField('Organization', validators=[Optional(), Length(max=200)])
    city            = StringField('City', validators=[Optional(), Length(max=80)])
    state           = StringField('State', validators=[Optional(), Length(max=80)])
    message         = TextAreaField('Why do you want to join PAAI?', validators=[Optional(), Length(max=2000)])
    submit          = SubmitField('Submit Application')


# ─── CONTACT FORM ─────────────────────────────────────────────────────────────
CONTACT_SUBJECTS = [
    ('General Enquiry',     'General Enquiry'),
    ('Membership Question', 'Membership Question'),
    ('Partnership Proposal','Partnership Proposal'),
    ('Media & Press',       'Media & Press'),
    ('Advocacy Support',    'Advocacy Support'),
    ('Other',               'Other'),
]

class ContactForm(FlaskForm):
    name    = StringField('Your Name', validators=[DataRequired(), Length(2, 120)])
    email   = EmailField('Email', validators=[DataRequired(), Email()])
    subject = SelectField('Subject', choices=CONTACT_SUBJECTS)
    message = TextAreaField('Message', validators=[DataRequired(), Length(10, 3000)])
    submit  = SubmitField('Send Message')


# ─── NEWS POST ────────────────────────────────────────────────────────────────
NEWS_CATEGORIES = [
    ('Policy Win',  'Policy Win'),
    ('Community',   'Community'),
    ('Research',    'Research'),
    ('Partnership', 'Partnership'),
    ('Awareness',   'Awareness'),
    ('Event',       'Event'),
]

class NewsForm(FlaskForm):
    title        = StringField('Title', validators=[DataRequired(), Length(5, 250)])
    category     = SelectField('Category', choices=NEWS_CATEGORIES)
    excerpt      = TextAreaField('Excerpt (max 500 chars)', validators=[Optional(), Length(max=500)])
    content      = TextAreaField('Content (HTML allowed)', validators=[DataRequired()])
    cover_image  = FileField('Cover Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    is_published = BooleanField('Publish immediately')
    submit       = SubmitField('Save Post')


# ─── EVENT ────────────────────────────────────────────────────────────────────
EVENT_TYPES = [
    ('Webinar',     'Webinar'),
    ('Conference',  'Conference'),
    ('Workshop',    'Workshop'),
    ('Campaign',    'Campaign'),
    ('Seminar',     'Seminar'),
]

class EventForm(FlaskForm):
    title             = StringField('Event Title', validators=[DataRequired(), Length(5, 250)])
    event_type        = SelectField('Type', choices=EVENT_TYPES)
    description       = TextAreaField('Description', validators=[Optional()])
    location          = StringField('Location', validators=[Optional(), Length(max=300)])
    event_date        = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    capacity          = StringField('Capacity (leave blank for unlimited)', validators=[Optional()])
    is_free           = BooleanField('Free Event', default=True)
    registration_link = StringField('Registration Link', validators=[Optional(), Length(max=500)])
    cover_image       = FileField('Cover Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    is_published      = BooleanField('Publish Event', default=True)
    submit            = SubmitField('Save Event')


# ─── RESOURCE ─────────────────────────────────────────────────────────────────
RESOURCE_CATEGORIES = [
    ('Patient Rights',  'Patient Rights'),
    ('Insurance',       'Insurance'),
    ('Mental Health',   'Mental Health'),
    ('Rare Disease',    'Rare Disease'),
    ('Caregiver',       'Caregiver'),
    ('Legal',           'Legal'),
    ('General',         'General'),
]

RESOURCE_TYPES = [
    ('PDF',     'PDF'),
    ('Video',   'Video'),
    ('Article', 'Article'),
    ('Toolkit', 'Toolkit'),
]

class ResourceForm(FlaskForm):
    title           = StringField('Title', validators=[DataRequired(), Length(5, 250)])
    category        = SelectField('Category', choices=RESOURCE_CATEGORIES)
    resource_type   = SelectField('Resource Type', choices=RESOURCE_TYPES)
    description     = TextAreaField('Description', validators=[Optional()])
    file_upload     = FileField('Upload File', validators=[FileAllowed(['pdf', 'doc', 'docx'])])
    external_url    = StringField('Or External URL', validators=[Optional(), Length(max=500)])
    language        = SelectField('Language', choices=[
        ('English','English'), ('Hindi','Hindi'), ('Tamil','Tamil'),
        ('Telugu','Telugu'), ('Marathi','Marathi'), ('Bengali','Bengali'),
    ])
    is_published    = BooleanField('Publish', default=True)
    submit          = SubmitField('Save Resource')


# ─── FAQ ──────────────────────────────────────────────────────────────────────
class FAQForm(FlaskForm):
    question    = StringField('Question', validators=[DataRequired(), Length(5, 500)])
    answer      = TextAreaField('Answer', validators=[DataRequired()])
    category    = SelectField('Category', choices=[
        ('Membership','Membership'), ('Programs','Programs'),
        ('Resources','Resources'), ('General','General'),
    ])
    keywords    = StringField('Keywords (comma-separated)', validators=[Optional(), Length(max=500)])
    order       = StringField('Display Order', validators=[Optional()])
    is_active   = BooleanField('Active', default=True)
    submit      = SubmitField('Save FAQ')
