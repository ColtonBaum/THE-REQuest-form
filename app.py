from flask import Flask
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from models import db
from public import public_bp
from admin import admin_bp
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO

# For timezone conversion filter
default_tz = 'America/Denver'
from datetime import datetime
import pytz

load_dotenv()  # Load variables from .env if present

# Create Flask app
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Jinja2 filter to convert UTC datetime to local Mountain Time
@app.template_filter('localtime')
def localtime(dt_obj, tz_name=default_tz, fmt='%m/%d/%Y %I:%M %p'):
    """Convert an aware UTC datetime to local tz and format."""
    # ensure UTC tzinfo
    if dt_obj.tzinfo is None:
        utc_dt = dt_obj.replace(tzinfo=pytz.utc)
    else:
        utc_dt = dt_obj.astimezone(pytz.utc)
    local_dt = utc_dt.astimezone(pytz.timezone(tz_name))
    return local_dt.strftime(fmt)

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

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)

# Expose socketio instance for other modules (like public.py)
app.socketio = socketio

# Run the app with SocketIO
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created
    socketio.run(app, host="0.0.0.0", port=8080)
