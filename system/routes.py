import os
import secrets
from werkzeug.utils import secure_filename
from flask import render_template, url_for, flash, redirect, request, abort
from system import app, db, bcrypt
from system.forms import RegistrationForm, LoginForm, DriveForm, UpdateResumeForm, UpdateStudentProfileForm
from system.models import User, Company, Student, Drive, Application
from flask_login import login_user, current_user, logout_user, login_required
from utils.decorator import roles_required

def save_resume(form_file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    resume_fn = random_hex + f_ext
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_fn)
    form_file.save(resume_path)
    return resume_fn

@app.route('/')
def home():
    total_companies = Company.query.count()
    total_drives = Drive.query.count()
    total_placed_students = Application.query.filter_by(status='Selected').count()
    placement_percentage = (Application.query.filter_by(status='Selected').count() // Application.query.count()) * 100
    print(total_placed_students)
    if current_user.is_authenticated:
        if current_user.role == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'Company':
            return redirect(url_for('company_dashboard'))
        elif current_user.role == 'Student':
            return redirect(url_for('student_dashboard'))
    
    return render_template('home.html',total_companies=total_companies,total_drives=total_drives,total_placed_students=total_placed_students,placement_percentage=placement_percentage)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        
        if form.role.data == 'Company':
            company = Company(user_id=user.id, name=form.company_name.data, hr_contact=form.hr_contact.data, website=form.company_website.data)
            db.session.add(company)
        elif form.role.data == 'Student':
            resume_file = None
            if form.resume.data:
                print(form.resume.data)
                resume_file = save_resume(form.resume.data)
            student = Student(user_id=user.id, name=form.student_name.data, resume_file=resume_file)
            db.session.add(student)
        # COmmitting it
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('login'))
                
            if user.role == 'Company' and not user.company_profile.is_approved:
                flash('Your company account is pending Admin approval.', 'info')
                return redirect(url_for('login'))
                
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/company_dashboard')
@login_required
@roles_required('Company')
def company_dashboard():
    company = current_user.company_profile
    drives = Drive.query.filter_by(company_id=company.id).order_by(Drive.created_at.desc()).all()
    return render_template('company/dashboard.html', title='Company Dashboard', company=company, drives=drives)

@app.route('/company/create_drive', methods=['GET', 'POST'])
@login_required
@roles_required('Company')
def create_drive():
    company = current_user.company_profile
    if not company.is_approved:
        flash('You cannot create drives until your account is approved by an Admin.', 'danger')
        return redirect(url_for('company_dashboard'))
        
    form = DriveForm()
    if form.validate_on_submit():
        drive = Drive(
            title=form.title.data,
            description=form.description.data,
            eligibility=form.eligibility.data,
            deadline=form.deadline.data,
            company_id=company.id,
            status='Pending'
        )
        db.session.add(drive)
        db.session.commit()
        flash('Placement drive created! Waiting for admin approval.', 'success')
        return redirect(url_for('company_dashboard'))
    return render_template('company/create_drive.html', title='Create Drive', form=form)

@app.route('/company/drive/<int:drive_id>')
@login_required
@roles_required('Company')
def view_drive_applications(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    if drive.company_id != current_user.company_profile.id:
        abort(403)
    applications = Application.query.filter_by(drive_id=drive.id).all()
    return render_template('company/drive_applications.html', title=drive.title, drive=drive, applications=applications)

@app.route('/company/drive/<int:drive_id>/close')
@login_required
@roles_required('Company')
def close_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    if drive.company_id != current_user.company_profile.id:
        abort(403)
    drive.status = 'Closed'
    db.session.commit()
    flash(f'Drive {drive.title} closed.', 'info')
    return redirect(url_for('company_dashboard'))

@app.route('/company/application/<int:app_id>/status/<string:status>')
@login_required
@roles_required('Company')
def update_application_status(app_id, status):
    if status not in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
        abort(400)
    application = Application.query.get_or_404(app_id)
    if application.drive.company_id != current_user.company_profile.id:
        abort(403)
    application.status = status
    db.session.commit()
    flash(f"Application status updated to {status}", 'success')
    return redirect(url_for('view_drive_applications', drive_id=application.drive_id))

# --- Student Dashboards ---
@app.route('/student_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('Student')
def student_dashboard():
    # Only show approved company drives
    drives = Drive.query.filter_by(status='Approved').order_by(Drive.created_at.desc()).all()
    # Get user applications
    student = current_user.student_profile
    applications = Application.query.filter_by(student_id=student.id).all()
    applied_drive_ids = [app.drive_id for app in applications]
    
    form = UpdateResumeForm()
    if form.validate_on_submit() and 'submit_resume' in request.form:
        if form.resume.data:
            if student.resume_file:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], student.resume_file)
                if os.path.exists(old_path):
                    os.remove(old_path)
            resume_file = save_resume(form.resume.data)
            student.resume_file = resume_file
            db.session.commit()
            flash('Your resume has been updated!', 'success')
            return redirect(url_for('student_dashboard'))
    
    return render_template('student/dashboard.html', title='Student Dashboard', drives=drives, applications=applications, applied_drive_ids=applied_drive_ids, form=form)

@app.route('/student/delete_resume', methods=['POST'])
@login_required
@roles_required('Student')
def delete_resume():
    student = current_user.student_profile
    if student.resume_file:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], student.resume_file)
        if os.path.exists(old_path):
            os.remove(old_path)
        student.resume_file = None
        db.session.commit()
        flash('Your resume has been deleted.', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/student/edit_profile', methods=['GET', 'POST'])
@login_required
@roles_required('Student')
def edit_student_profile():
    form = UpdateStudentProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.student_profile.name = form.student_name.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('student_dashboard'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.student_name.data = current_user.student_profile.name
    return render_template('student/edit_profile.html', title='Edit Profile', form=form)

@app.route('/student/apply/<int:drive_id>')
@login_required
@roles_required('Student')
def apply_to_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    student = current_user.student_profile
    
    # Check if drive is approved and not closed
    if drive.status != 'Approved':
        flash('You cannot apply to this placement drive.', 'danger')
        return redirect(url_for('student_dashboard'))
        
    # Check if already applied
    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing_app:
        flash('You have already applied to this drive.', 'warning')
        return redirect(url_for('student_dashboard'))
        
    application = Application(student_id=student.id, drive_id=drive.id)
    db.session.add(application)
    db.session.commit()
    flash(f'Successfully applied to {drive.title} at {drive.company.name}!', 'success')
    return redirect(url_for('student_dashboard'))

# --- Dashboards ---
@app.route('/admin_dashboard')
@login_required
@roles_required('Admin')
def admin_dashboard():
    # Statistics
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = Drive.query.count()
    total_applications = Application.query.count()
    
    # Lists
    pending_companies = Company.query.filter_by(is_approved=False).all()
    approved_companies = Company.query.filter_by(is_approved=True).all()
    pending_drives = Drive.query.filter_by(status='Pending').all()
    all_drives = Drive.query.all()
    all_students = Student.query.all()
    non_admin_users = User.query.filter(User.role != 'Admin').all()
    
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                           total_students=total_students, total_companies=total_companies,
                           total_drives=total_drives, total_applications=total_applications,
                           pending_companies=pending_companies, approved_companies=approved_companies,
                           pending_drives=pending_drives, all_drives=all_drives,
                           all_students=all_students, all_users=non_admin_users)

@app.route('/admin/approve_company/<int:company_id>')
@login_required
@roles_required('Admin')
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    flash(f'Company {company.name} approved successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_company/<int:company_id>')
@login_required
@roles_required('Admin')
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    user = company.user
    db.session.delete(company)
    db.session.delete(user)
    db.session.commit()
    flash(f'Company registration rejected and removed.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/approve_drive/<int:drive_id>')
@login_required
@roles_required('Admin')
def approve_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'Approved'
    db.session.commit()
    flash(f'Placement drive "{drive.title}" approved.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_drive/<int:drive_id>')
@login_required
@roles_required('Admin')
def reject_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash('Placement drive rejected and deleted.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_user/<int:user_id>')
@login_required
@roles_required('Admin')
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'Admin':
        flash('Cannot modify admin accounts.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated/blacklisted'
    flash(f'User account {status}.', 'info')
    return redirect(url_for('admin_dashboard'))