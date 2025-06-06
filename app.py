# app.py

from flask import Flask
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from models import db               # your SQLAlchemy instance
from public import public_bp        # public blueprint
from admin import admin_bp          # admin blueprint
import os
from dotenv import load_dotenv
load_dotenv()  # load .env file

# Create Flask app
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# PostgreSQL connection string from DigitalOcean
app.config.update({
    "SECRET_KEY": "your-secret-key",  # Replace with a real secret key
    "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL"),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "WTF_CSRF_ENABLED": True,
    "WTF_CSRF_TIME_LIMIT": None,  # Tokens never expire
})

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
app.jinja_env.globals['csrf_token'] = generate_csrf

# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures PostgreSQL tables are created if missing
    app.run(host="0.0.0.0", port=8080)

