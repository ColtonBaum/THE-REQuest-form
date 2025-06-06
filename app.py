# app.py

from flask import Flask
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from models import db               # your SQLAlchemy instance
from public import public_bp        # public blueprint
from admin import admin_bp          # admin blueprint

# Create Flask app
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.config.update({
    "SECRET_KEY": "your-secret-key",         # replace with a real secret
    "SQLALCHEMY_DATABASE_URI": "sqlite:///requests.db",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "WTF_CSRF_ENABLED": True,
    "WTF_CSRF_TIME_LIMIT": None,             # <-- tokens never expire
})

# Initialize extensions
db.init_app(app)                           # bind SQLAlchemy to this app
csrf = CSRFProtect(app)                     # enable CSRF protection
app.jinja_env.globals['csrf_token'] = generate_csrf  # expose csrf_token() in Jinja

# Register blueprints
app.register_blueprint(public_bp)            # handles '/' and '/submit'
app.register_blueprint(admin_bp)             # handles '/admin/*'

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8080)

