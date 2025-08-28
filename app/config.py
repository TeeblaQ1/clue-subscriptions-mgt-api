import os
from dotenv import load_dotenv

# load variables from .env into os.environ
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    # i'm using sqlite for simplicity but the same principle applies to MySQL/MariaDB
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///subscriptions.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.environ.get("JWT_SECRET", "jwt-secret")
