from datetime import datetime, date, time
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from system import db

class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(120),unique=True,nullable=False)
    name = db.Column(db.String(120),nullable=False)
    iamge_file = db.String(db.String(20),nullable=False,default='default.jpg')
    password_hash = db.Column(db.String(128),nullable=False)
    role = db.Column(db.String(20),nullable=False) # Admin or Doctor or patient
    contact = db.Column(db.String(120))
    is_active = db.Column(db.Boolean,default=True) # if any doctor is blacklisted

    # relationships
    doctor = db.relationship('Doctor',uselist=False,back_populates='user')
    patient = db.relationship('Patient',uselist=False,back_populates='user')

    def __repr__(self):
        return f'{self.email},{self.name},{self.role},{self.contact}'

    def set_password(self,passowrd):
        self.password_hash = generate_password_hash(passowrd)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    doctors = db.relationship("Doctor", back_populates="department")

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer,primary=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    department_id = db.Column(db.Integer,db.ForeignKey('departments.id'))
    specialization = db.Column(db.String(120))
    bio = db.Column(db.Text)
    user = db.relationship('User',back_populates='doctor')
    department = db.relationship("Department", back_populates="doctors")
    availabilities = db.relationship("Availability", back_populates="doctor")
    appointments = db.relationship("Appointment", back_populates="doctor")

class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    user = db.relationship("User", back_populates="patient")
    appointments = db.relationship("Appointment", back_populates="patient")

class Availability(db.Model):
    __tablename__ = "availabilities"
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    doctor = db.relationship("Doctor", back_populates="availabilities")


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default="Booked")  # Booked, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc))

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    treatment = db.relationship("Treatment", back_populates="appointment", uselist=False)

class Treatment(db.Model):
    __tablename__ = "treatments"
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointment = db.relationship("Appointment", back_populates="treatment")