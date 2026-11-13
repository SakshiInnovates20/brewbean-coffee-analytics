import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly resolve root directory .env file path
basedir = Path(__file__).resolve().parent.parent
env_file = basedir / '.env'

# Load environment variables with override=True to ensure .env changes apply dynamically
load_dotenv(dotenv_path=env_file, override=True)

class Config:
    """
    Application configuration class.
    Loads settings from root .env file with clean string stripping and integer conversion.
    """
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-brewbean').strip()
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development').strip()
    DEBUG = (FLASK_ENV == 'development')

    # MySQL Database settings from environment variables
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1').strip()
    DB_PORT = int(str(os.environ.get('DB_PORT', 3306)).strip())
    DB_USER = os.environ.get('DB_USER', 'root').strip()
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '').strip()
    DB_NAME = os.environ.get('DB_NAME', 'brewbean_analytics').strip()

