import os
from flask import Flask
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_socketio import SocketIO
from dotenv import load_dotenv
import pytz
from datetime import datetime

from models import db
from public import public_bp

load_dotenv()  # Load .env into environment

app = Flask(__name__, template_folder="templates", static_folder="static")

# Jinja2 filter to convert UTC datetime to local Mountain Time
@app.template_filter('localtime')
def localtime(dt_obj, tz_name='America/Denver', fmt='%m/%d/%Y %I:%M %p'):
    if dt_obj.tzinfo is None:
        utc_dt = dt_obj.replace(tzinfo=pytz.utc)
    else:
        utc_dt = dt_obj.astimezone(pytz.utc)
    local_dt = utc_dt.astimezone(pytz.timezone(tz_name))
    return local_dt.strftime(fmt)

# Configuration
db_uri = os.environ.get("DATABASE_URL")
if not db_uri:
    raise RuntimeError("DATABASE_URL environment variable not set")

# --- NEW/CHANGED: normalize old-style postgres:// URLs (SQLAlchemy expects postgresql://)
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

# --- NEW/CHANGED: resilient connection pool settings to avoid "SSL connection has been closed unexpectedly"
engine_options = {
    # Key fix: verify connection is alive before using it; reconnect if it's dead
    "pool_pre_ping": True,

    # Avoid long-idle connections being reused after the DB/network drops them
    "pool_recycle": 300,  # seconds (5 minutes). Tune as needed.

    # Optional but helpful defaults
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
}

# If your provider requires SSL (common), forcing sslmode=require is usually safe.
# If your DATABASE_URL already includes sslmode=..., psycopg2 will use that.
if "sslmode=" not in db_uri:
    engine_options["connect_args"] = {
        "sslmode": "require",
        # TCP keepalives help prevent silent idle drops
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }

app.config.update({
    "SECRET_KEY": os.environ.get("SECRET_KEY", "your-secret-key"),
    "SQLALCHEMY_DATABASE_URI": db_uri,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,

    # --- NEW/CHANGED
    "SQLALCHEMY_ENGINE_OPTIONS": engine_options,
})

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# CSRF protection
csrf = CSRFProtect(app)

# Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Import admin *after* CSRF is set up
from admin import admin_bp

# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)

# Expose socketio on app
app.socketio = socketio

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, host="0.0.0.0", port=8080)
