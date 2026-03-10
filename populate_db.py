from system import app, bcrypt
from system.models import db, User, Company, Student, Drive, Application
from datetime import datetime, timedelta

def populate_db():
    with app.app_context():
        # Ensure tables exist (will not overwrite existing data)
        print("Ensuring tables are created...")
        db.create_all()

        print("Checking if Admin exists...")
        admin_user = User.query.filter_by(role='Admin').first()
        if not admin_user:
            print("No admin found. Creating default admin...")
            admin_user = User(username='admin', email='admin@institute.edu', role='Admin')
            admin_user.password_hash = bcrypt.generate_password_hash('Admin@123').decode('utf-8')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin created successfully.")
        else:
            print(f"Admin already exists: {admin_user.username}")

        print("Checking if dummy data already exists...")
        if User.query.filter_by(username='company1').first():
            print("Dummy data already exists. Skipping population to avoid duplicates.")
            return

        print("Generating dummy data...")

        # Create Companies
        company_users = []
        companies = [
            {'name': 'TechCorp Solutions', 'hr_contact': 'hr@techcorp.com', 'website': 'www.techcorp.com'},
            {'name': 'Global Innovations', 'hr_contact': 'careers@globalinnovations.com', 'website': 'www.globalinnovations.com'},
            {'name': 'Datawiz Analytics', 'hr_contact': 'jobs@datawiz.com', 'website': 'www.datawiz.com'}
        ]

        created_companies = []
        for i, comp_data in enumerate(companies):
            comp_user = User(username=f'company{i+1}', email=f'company{i+1}@example.com', role='Company')
            comp_user.password_hash = bcrypt.generate_password_hash('company123').decode('utf-8')
            db.session.add(comp_user)
            db.session.flush() # Get the user ID

            company = Company(
                user_id=comp_user.id,
                name=comp_data['name'],
                hr_contact=comp_data['hr_contact'],
                website=comp_data['website'],
                is_approved=True # Approving them automatically for dummy data
            )
            db.session.add(company)
            created_companies.append(company)

        # Create Students
        student_users = []
        students = [
            {'name': 'Rajesh', 'contact': '1234567890', 'resume_file': 'rajesh_resume.pdf'},
            {'name': 'Bob Johnson', 'contact': '9876543210', 'resume_file': 'bob_resume.pdf'},
            {'name': 'Soham', 'contact': '5551234567', 'resume_file': 'Soham_resume.pdf'},
            {'name': 'Prince', 'contact': '7778889990', 'resume_file': 'prince_resume.pdf'}
        ]

        created_students = []
        for i, std_data in enumerate(students):
            std_user = User(username=f'student{i+1}', email=f'student{i+1}@example.com', role='Student')
            std_user.password_hash = bcrypt.generate_password_hash('student123').decode('utf-8')
            db.session.add(std_user)
            db.session.flush() # Get the user ID

            student = Student(
                user_id=std_user.id,
                name=std_data['name'],
                contact=std_data['contact'],
                resume_file=std_data['resume_file']
            )
            db.session.add(student)
            created_students.append(student)

        # Create Placement Drives
        drives = [
            {
                'company': created_companies[0],
                'title': 'Software Engineer Trainee',
                'description': 'Looking for fresh graduates with strong Python and web development skills.',
                'eligibility': 'B.Tech/BE in CS/IT. CGPA > 7.0',
                'deadline': datetime.now() + timedelta(days=15),
                'status': 'Approved'
            },
            {
                'company': created_companies[1],
                'title': 'Data Analyst',
                'description': 'Entry-level data analyst position requiring strong SQL and Excel skills.',
                'eligibility': 'Any degree. Strong analytical skills.',
                'deadline': datetime.now() + timedelta(days=10),
                'status': 'Approved'
            },
            {
                'company': created_companies[2],
                'title': 'Frontend Developer',
                'description': 'Seeking frontend developers proficient in React and UI/UX design.',
                'eligibility': 'B.Tech/BE in any discipline. Portfolio required.',
                'deadline': datetime.now() + timedelta(days=5),
                'status': 'Approved'
            },
            {
                'company': created_companies[0],
                'title': 'Backend Developer (Pending)',
                'description': 'Seeking backend developer with Node.js experience.',
                'eligibility': 'B.Tech/BE in CS/IT.',
                'deadline': datetime.now() + timedelta(days=20),
                'status': 'Pending'
            }
        ]

        created_drives = []
        for drive_data in drives:
            drive = Drive(
                company_id=drive_data['company'].id,
                title=drive_data['title'],
                description=drive_data['description'],
                eligibility=drive_data['eligibility'],
                deadline=drive_data['deadline'],
                status=drive_data['status']
            )
            db.session.add(drive)
            created_drives.append(drive)

        db.session.flush() # Ensure drives are assigned IDs

        # Create Applications
        applications = [
            {'student': created_students[0], 'drive': created_drives[0], 'status': 'Applied'},
            {'student': created_students[1], 'drive': created_drives[0], 'status': 'Shortlisted'},
            {'student': created_students[2], 'drive': created_drives[0], 'status': 'Applied'},
            
            {'student': created_students[0], 'drive': created_drives[1], 'status': 'Selected'},
            {'student': created_students[3], 'drive': created_drives[1], 'status': 'Applied'},
            
            {'student': created_students[1], 'drive': created_drives[2], 'status': 'Rejected'},
            {'student': created_students[2], 'drive': created_drives[2], 'status': 'Applied'},
        ]

        for app_data in applications:
            application = Application(
                student_id=app_data['student'].id,
                drive_id=app_data['drive'].id,
                status=app_data['status']
            )
            db.session.add(application)

        # Commit all changes
        try:
            db.session.commit()
            print("Successfully populated the database with dummy data!")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    populate_db()
