from flask import Flask
from config import config
from .extensions import db, migrate, login_manager, bcrypt, csrf, mail

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Login manager config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to access this page.'
    login_manager.login_message_category = 'info'

    # Import models so SQLAlchemy registers all tables
    from . import models
    
    # Register blueprints
    from .routes.public import public_bp
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.admin import admin_bp
    from .routes.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Error handlers
    from .utils.errors import register_error_handlers
    register_error_handlers(app)

    # Create upload directory
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
