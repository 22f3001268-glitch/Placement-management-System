from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, DateField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from system.models import User
from flask_login import current_user
class RegistrationForm(FlaskForm):
    role = SelectField('Register As', choices=[('Student', 'Student'), ('Company', 'Company')], validators=[DataRequired()])
    username = StringField('Username (Login ID)', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Role specific fields
    student_name = StringField('Full Name (For Students)', validators=[Length(max=120)])
    resume = FileField('Resume (PDF/Doc) (For Students)', validators=[FileAllowed(['pdf', 'doc', 'docx'])])
    
    company_name = StringField('Company Name (For Companies)', validators=[Length(max=120)])
    hr_contact = StringField('HR Contact Name (For Companies)', validators=[Length(max=120)])
    company_website = StringField('Company Website (For Companies)', validators=[Length(max=120)])
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
            
    def validate(self, **kwargs):
        initial_validation = super(RegistrationForm, self).validate()
        if not initial_validation:
            return False
            
        if self.role.data == 'Student' and not self.student_name.data:
            self.student_name.errors.append('Full name is required for students.')
            return False
            
        if self.role.data == 'Company' and not self.company_name.data:
            self.company_name.errors.append('Company name is required for companies.')
            return False
            
        return True

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class DriveForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    eligibility = TextAreaField('Eligibility Criteria')
    deadline = DateField('Application Deadline (YYYY-MM-DD)')
    submit = SubmitField('Create Placement Drive')

class UpdateResumeForm(FlaskForm):
    resume = FileField('Upload New Resume', validators=[DataRequired(), FileAllowed(['pdf', 'doc', 'docx'])])
    submit_resume = SubmitField('Upload Resume')

class UpdateStudentProfileForm(FlaskForm):
    username = StringField('Username (Login ID)', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    student_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')