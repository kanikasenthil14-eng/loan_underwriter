import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kredpilot-secret-key-change-in-prod')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/kredpilot_ai')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@kredpilot.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
