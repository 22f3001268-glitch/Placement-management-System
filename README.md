# Placement Management System (Campus Connect)

Campus Connect is a comprehensive Placement Management System portal designed to streamline the recruitment process. It serves as a unified platform connecting Students, Companies, and the College Administration (Admin) to facilitate seamless placement drives, job applications, and recruitment statistics tracking.

## Features

### 👤 Admin
- **User Management**: Approve and manage student and company registrations.
- **Placement Oversight**: Monitor and manage ongoing placement drives and job postings.
- **Analytics & Tracking**: View overall placement statistics, application statuses, and system metrics.

### 🏢 Company
- **Registration**: Register corporate profiles on the portal.
- **Job Postings & Drives**: Create and manage placement drives and job descriptions.
- **Applicant Tracking**: View student applications, review profiles, and shortlist/hire candidates.

### 🎓 Student
- **Profile Building**: Create and maintain a detailed academic and professional profile.
- **Job Discovery**: Browse available placement drives and job postings.
- **Application Management**: Apply for jobs and track ongoing application statuses.

## Tech Stack

**Backend:**
- [Python]
- [Flask](Web Framework)
- Flask-SQLAlchemy (ORM for Database interactions)
- Flask-Login & Flask-Bcrypt (Authentication & Security)
- Flask-WTF & WTForms (Form Handling & Validation)

**Database:**
- SQLite

**Frontend:**
- HTML5 / CSS3
- [Bootstrap] (Responsive UI Styling)

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/22f3001268-glitch/Placement-management-System.git
   cd Placement-management-system
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**
   ```bash
   python run.py
   ```
   The application will start running at `http://127.0.0.1:5000/`.

## Project Structure

```text
Placement-management-system/
│
├── system/                 # Main application package
│   ├── __init__.py         # App initialization and configuration
│   ├── models.py           # Database models (SQLAlchemy)
│   ├── routes.py           # Application routes and controllers
│   ├── forms.py            # WTForms classes for user input
│   ├── static/             # Static assets (CSS, JS, Images)
│   └── templates/          # Jinja2 HTML templates
│
├── instance/               # Instance folder (contains the SQLite database file)
├── utils/                  # Utility functions and helper scripts
├── requirements.txt        # Python package dependencies
├── run.py                  # Entry point to run the Flask application
└── README.md               # Project documentation
```
