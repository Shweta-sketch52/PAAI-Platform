from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone         = db.Column(db.String(20))
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default='user')
    is_active     = db.Column(db.Boolean, default=True)
    city          = db.Column(db.String(80))
    state         = db.Column(db.String(80))
    profile_pic   = db.Column(db.String(256), default='default_avatar.png')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)

    # Specify foreign_keys explicitly to avoid ambiguity with 'reviewed_by'
    membership = db.relationship(
        'MembershipApplication',
        foreign_keys='MembershipApplication.user_id',
        backref='user',
        uselist=False
    )
    saved_resources = db.relationship('SavedResource', backref='user', lazy='dynamic')
    event_regs      = db.relationship('EventRegistration', backref='user', lazy='dynamic')
    notifications   = db.relationship('Notification', backref='user', lazy='dynamic')
    chat_sessions   = db.relationship('ChatSession', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_initials(self):
        parts = self.full_name.strip().split()
        return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else '')).upper()

    def __repr__(self):
        return f'<User {self.email}>'


class MembershipApplication(db.Model):
    __tablename__ = 'membership_applications'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    full_name       = db.Column(db.String(120), nullable=False)
    email           = db.Column(db.String(150), nullable=False)
    phone           = db.Column(db.String(20))
    membership_type = db.Column(db.String(60), nullable=False)
    organization    = db.Column(db.String(200))
    city            = db.Column(db.String(80))
    state           = db.Column(db.String(80))
    message         = db.Column(db.Text)
    status          = db.Column(db.String(20), default='pending')
    admin_notes     = db.Column(db.Text)
    reviewed_by     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at     = db.Column(db.DateTime)
    submitted_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Explicit relationship to the reviewer
    reviewer = db.relationship(
        'User',
        foreign_keys=[reviewed_by]
    )

    def __repr__(self):
        return f'<Membership {self.full_name} [{self.status}]>'


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(150), nullable=False)
    subject    = db.Column(db.String(200), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    replied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contact {self.name}: {self.subject}>'


class NewsPost(db.Model):
    __tablename__ = 'news_posts'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(250), nullable=False)
    slug         = db.Column(db.String(280), unique=True, nullable=False)
    category     = db.Column(db.String(60))
    excerpt      = db.Column(db.String(500))
    content      = db.Column(db.Text, nullable=False)
    cover_image  = db.Column(db.String(256))
    author_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, onupdate=datetime.utcnow)

    author = db.relationship('User', foreign_keys=[author_id])

    def __repr__(self):
        return f'<News {self.title}>'


class Event(db.Model):
    __tablename__ = 'events'

    id                = db.Column(db.Integer, primary_key=True)
    title             = db.Column(db.String(250), nullable=False)
    event_type        = db.Column(db.String(60))
    description       = db.Column(db.Text)
    location          = db.Column(db.String(300))
    event_date        = db.Column(db.DateTime, nullable=False)
    end_date          = db.Column(db.DateTime)
    capacity          = db.Column(db.Integer)
    is_free           = db.Column(db.Boolean, default=True)
    registration_link = db.Column(db.String(500))
    cover_image       = db.Column(db.String(256))
    is_published      = db.Column(db.Boolean, default=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic')

    @property
    def registered_count(self):
        return self.registrations.count()

    def __repr__(self):
        return f'<Event {self.title}>'


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id      = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    attended      = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='uq_user_event'),
    )


class Resource(db.Model):
    __tablename__ = 'resources'

    id             = db.Column(db.Integer, primary_key=True)
    title          = db.Column(db.String(250), nullable=False)
    category       = db.Column(db.String(80))
    description    = db.Column(db.Text)
    resource_type  = db.Column(db.String(40))
    file_path      = db.Column(db.String(500))
    external_url   = db.Column(db.String(500))
    language       = db.Column(db.String(40), default='English')
    is_published   = db.Column(db.Boolean, default=True)
    download_count = db.Column(db.Integer, default=0)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    saved_by = db.relationship('SavedResource', backref='resource', lazy='dynamic')

    def __repr__(self):
        return f'<Resource {self.title}>'


class SavedResource(db.Model):
    __tablename__ = 'saved_resources'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    saved_at    = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'resource_id', name='uq_user_resource'),
    )


class Notification(db.Model):
    __tablename__ = 'notifications'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.String(500), nullable=False)
    link       = db.Column(db.String(300))
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FAQ(db.Model):
    __tablename__ = 'faqs'

    id         = db.Column(db.Integer, primary_key=True)
    question   = db.Column(db.String(500), nullable=False)
    answer     = db.Column(db.Text, nullable=False)
    category   = db.Column(db.String(80))
    keywords   = db.Column(db.String(500))
    is_active  = db.Column(db.Boolean, default=True)
    order      = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FAQ {self.question[:50]}>'


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), unique=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages   = db.relationship('ChatMessage', backref='session', lazy='dynamic')


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    role       = db.Column(db.String(10))
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
