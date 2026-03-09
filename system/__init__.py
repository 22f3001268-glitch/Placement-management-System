from flask import Flask
from system.models import db, User
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'placement_portal_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'resumes')

# Make sure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from system import routes

with app.app_context():
    db.create_all()
    
    # Initialize Admin User Default
    if not User.query.filter_by(role='Admin').first():
        admin_pass = bcrypt.generate_password_hash('Admin@123').decode('utf-8')
        admin = User(username='admin', email='admin@institute.edu', password_hash=admin_pass, role='Admin')
        db.session.add(admin)
        db.session.commit()
