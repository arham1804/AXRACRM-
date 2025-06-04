import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from flask_socketio import SocketIO

# Load environment variables from .env file (optional but recommended)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with model_class Base
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Stability configs
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Correctly set SQLALCHEMY_DATABASE_URI from environment variable with fallback
default_db_uri = (
    "postgresql://AXRATUTOR_owner:npg_Bb4qNCFDTXc1@"
    "ep-frosty-darkness-a1sjz40x-pooler.ap-southeast-1.aws.neon.tech/"
    "AXRATUTOR?sslmode=require&options=endpoint%3Dep-frosty-darkness-a1sjz40x-pooler"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", default_db_uri)

# Initialize SQLAlchemy with app
db.init_app(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models and create tables
with app.app_context():
    from models import Admin, Student, Teacher, TuitionAssignment, Demo, Feedback
    db.create_all()
    
    # Create default admin if it doesn't exist
    from models import Admin
    from werkzeug.security import generate_password_hash
    admin = Admin.query.filter_by(email="arham786@axratutor.com").first()
    if not admin:
        default_admin = Admin(
            name="Admin",
            email="arham786@axratutor.com",
            password_hash=generate_password_hash("Shazab786@")
        )
        db.session.add(default_admin)
        db.session.commit()
        logging.info("Default admin user created")

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import Admin
    return Admin.query.get(int(user_id))

# Import and register routes
from routes import *

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
