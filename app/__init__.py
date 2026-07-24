from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config

mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.routes.auth_routes import auth_bp
    from app.routes.customer_routes import customer_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        _init_admin(app)

    return app

def _init_admin(app):
    from app.models.user_model import UserModel
    existing = mongo.db.users.find_one({'email': app.config['ADMIN_EMAIL']})
    if not existing:
        hashed = bcrypt.generate_password_hash(app.config['ADMIN_PASSWORD']).decode('utf-8')
        mongo.db.users.insert_one({
            'name': 'Admin User',
            'email': app.config['ADMIN_EMAIL'],
            'password': hashed,
            'role': 'admin',
            'mobile': '0000000000',
            'created_at': __import__('datetime').datetime.utcnow()
        })
