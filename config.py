import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env file

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
