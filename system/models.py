from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Admin', 'Company', 'Student'
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    company_profile = db.relationship('Company', back_populates='user', uselist=False, cascade="all, delete-orphan")
    student_profile = db.relationship('Student', back_populates='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    hr_contact = db.Column(db.String(10))
    website = db.Column(db.String(120))
    is_approved = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', back_populates='company_profile')
    drives = db.relationship('Drive', back_populates='company', cascade="all, delete-orphan")

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(120))
    resume_file = db.Column(db.String(120))
    
    # Relationships
    user = db.relationship('User', back_populates='student_profile')
    applications = db.relationship('Application', back_populates='student', cascade="all, delete-orphan")

class Drive(db.Model):
    __tablename__ = 'drives'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Pending') # Pending, Approved, Closed
    created_at = db.Column(db.DateTime, server_default=func.now())
    
    # Relationships
    company = db.relationship('Company', back_populates='drives')
    applications = db.relationship('Application', back_populates='drive', cascade="all, delete-orphan")

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='Applied') # Applied, Shortlisted, Selected, Rejected
    application_date = db.Column(db.DateTime, server_default=func.now())
    
    # Ensuring one application per student per drive
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='_student_drive_uc'),)

    # Relationships
    student = db.relationship('Student', back_populates='applications')
    drive = db.relationship('Drive', back_populates='applications')