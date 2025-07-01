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

app.config.update({
    "SECRET_KEY": os.environ.get("SECRET_KEY", "your-secret-key"),
    "SQLALCHEMY_DATABASE_URI": db_uri,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    # WTForms CSRF is on by default; no need for explicit flags here
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
