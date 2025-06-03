import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database (SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///axra_tutor.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
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
