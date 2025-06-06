from flask import Flask
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from models import db
from public import public_bp
from admin import admin_bp
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env if present

# Create Flask app
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Get the database URI from environment
db_uri = os.environ.get("DATABASE_URL")
if not db_uri:
    raise RuntimeError("DATABASE_URL environment variable not set")

# Flask config
app.config.update({
    "SECRET_KEY": os.environ.get("SECRET_KEY", "your-secret-key"),  # Fallback if SECRET_KEY is not set
    "SQLALCHEMY_DATABASE_URI": db_uri,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "WTF_CSRF_ENABLED": True,
    "WTF_CSRF_TIME_LIMIT": None,
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
        db.create_all()  # Ensure tables are created
    app.run(host="0.0.0.0", port=8080)
