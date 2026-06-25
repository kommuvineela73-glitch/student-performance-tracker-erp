import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 🔐 Security Key (IMPORTANT for sessions & flash)
    SECRET_KEY = os.environ.get("SECRET_KEY") or "student_tracker_secret_key_2026"

    # 📦 Database (SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(BASE_DIR, "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 📁 Upload folder (safe + structured)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    # 🔥 Optional (recommended for real projects)
    JSON_SORT_KEYS = False