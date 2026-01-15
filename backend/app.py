"""
Saroj Acharya Portfolio - Flask Backend Application
Author: Saroj Acharya
Description: Complete backend API for portfolio website with database,
contact form handling, and project management.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import re
from functools import wraps
import logging
import smtplib
from email.message import EmailMessage

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS based on environment
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'sqlite:///saroj_portfolio.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    if os.getenv('FLASK_ENV', 'development') == 'production':
        raise ValueError('SECRET_KEY environment variable is not set. Please set it before running in production.')
    app.config['SECRET_KEY'] = 'dev-secret-key-change-this'
app.config['JSON_SORT_KEYS'] = False

# Initialize database
db = SQLAlchemy(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key for protecting admin endpoints
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'change-this-key-in-production')

def require_api_key(f):
    """Decorator to protect admin endpoints with API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != ADMIN_API_KEY:
            return jsonify({'error': 'Unauthorized. Invalid or missing API key.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ===== Database Models =====

class Contact(db.Model):
    """Model for contact form submissions"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


class Project(db.Model):
    """Model for portfolio projects"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    long_description = db.Column(db.Text, nullable=True)
    technologies = db.Column(db.String(500), nullable=False)
    live_url = db.Column(db.String(300), nullable=True)
    github_url = db.Column(db.String(300), nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    featured = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'long_description': self.long_description,
            'technologies': [t.strip() for t in self.technologies.split(',')],
            'live_url': self.live_url,
            'github_url': self.github_url,
            'image_url': self.image_url,
            'featured': self.featured,
            'created_at': self.created_at.isoformat()
        }


class Skill(db.Model):
    """Model for technical skills"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.Integer, default=70)
    order = db.Column(db.Integer, default=0)
    
    __table_args__ = (db.UniqueConstraint('category', 'name', name='unique_skill'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'proficiency': self.proficiency
        }


class Experience(db.Model):
    """Model for work experience"""
    __tablename__ = 'experiences'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'role': self.role,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description
        }


class Visitor(db.Model):
    """Model for tracking visitors"""
    __tablename__ = 'visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.String(500), nullable=True)
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)
    page = db.Column(db.String(100), default='/')


# ===== Utility Functions =====

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def rate_limit(limit_per_hour=10):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            recent_contacts = Contact.query.filter(
                Contact.ip_address == ip,
                Contact.created_at >= hour_ago
            ).count()
            
            if recent_contacts >= limit_per_hour:
                return jsonify({'error': 'Too many requests. Please try again later.'}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_visitor():
    """Log visitor information"""
    try:
        visitor = Visitor(
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            page=request.path
        )
        db.session.add(visitor)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging visitor: {e}")


# ===== API Routes =====

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Welcome to Saroj Acharya Portfolio API',
        'version': '1.0.0',
        'endpoints': {
            'contacts': '/api/contact (POST), /api/contacts (GET)',
            'projects': '/api/projects (GET, POST)',
            'skills': '/api/skills (GET), /api/skills/<category> (GET)',
            'experiences': '/api/experiences (GET)',
            'stats': '/api/stats (GET)'
        }
    })


# ===== Contact Routes =====

@app.route('/api/contact', methods=['POST', 'OPTIONS'])
@rate_limit(limit_per_hour=10)
def submit_contact():
    """Submit a contact form message"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({'error': 'Request body is empty'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()
        subject = data.get('subject', 'Portfolio Contact').strip()
        
        if not all([name, email, message]):
            return jsonify({'error': 'Missing required fields: name, email, message'}), 400
        
        if len(name) < 2 or len(name) > 100:
            return jsonify({'error': 'Name must be between 2 and 100 characters'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email address'}), 400
        
        if len(message) < 10 or len(message) > 5000:
            return jsonify({'error': 'Message must be between 10 and 5000 characters'}), 400
        
        # Create contact record
        contact = Contact(
            name=name,
            email=email,
            subject=subject,
            message=message,
            ip_address=request.remote_addr
        )
        
        db.session.add(contact)
        db.session.commit()
        
        logger.info(f"New contact submission from {email}")
        # Send notification email if mail configuration is provided
        try:
            mail_server = os.getenv('MAIL_SERVER')
            mail_port = int(os.getenv('MAIL_PORT', 587))
            mail_username = os.getenv('MAIL_USERNAME')
            mail_password = os.getenv('MAIL_PASSWORD')
            mail_use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
            mail_from = os.getenv('MAIL_DEFAULT_SENDER', mail_username)
            mail_to = os.getenv('MAIL_NOTIFY_TO', 'acharyasaroj9800@gmail.com')

            if mail_server and mail_username and mail_password and mail_to:
                msg = EmailMessage()
                msg['Subject'] = f"New contact form submission: {subject}"
                msg['From'] = mail_from
                msg['To'] = mail_to
                body = (
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Subject: {subject}\n\n"
                    f"Message:\n{message}\n\n"
                    f"IP: {contact.ip_address}\n"
                    f"Received at: {contact.created_at.isoformat()}"
                )
                msg.set_content(body)

                server = smtplib.SMTP(mail_server, mail_port, timeout=10)
                if mail_use_tls:
                    server.starttls()
                server.login(mail_username, mail_password)
                server.send_message(msg)
                server.quit()
                logger.info(f"Notification email sent to {mail_to}")
        except Exception as e:
            logger.error(f"Error sending contact notification email: {e}")
        
        return jsonify({
            'message': 'Thank you! Your message has been received. I will get back to you soon.',
            'contact': contact.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error submitting contact: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/contacts', methods=['GET'])
@require_api_key
def get_contacts():
    """Get all contacts (protected endpoint)"""
    try:
        contacts = Contact.query.order_by(Contact.created_at.desc()).all()
        return jsonify({
            'total': len(contacts),
            'contacts': [contact.to_dict() for contact in contacts]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/contact/<int:contact_id>/mark-read', methods=['PUT'])
@require_api_key
def mark_contact_read(contact_id):
    """Mark contact as read"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        contact.is_read = True
        db.session.commit()
        return jsonify({'message': 'Contact marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== Projects Routes =====

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        featured_only = request.args.get('featured', 'false').lower() == 'true'
        
        if featured_only:
            projects = Project.query.filter_by(featured=True).order_by(Project.order).all()
        else:
            projects = Project.query.order_by(Project.order).all()
        
        return jsonify({
            'total': len(projects),
            'projects': [project.to_dict() for project in projects]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get single project details"""
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify(project.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Project not found'}), 404


@app.route('/api/projects', methods=['POST'])
@require_api_key
def add_project():
    """Add a new project"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['title', 'description', 'technologies']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        project = Project(
            title=data['title'],
            description=data['description'],
            long_description=data.get('long_description'),
            technologies=data['technologies'],
            live_url=data.get('live_url'),
            github_url=data.get('github_url'),
            image_url=data.get('image_url'),
            featured=data.get('featured', False)
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify(project.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@require_api_key
def update_project(project_id):
    """Update a project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        if 'title' in data:
            project.title = data['title']
        if 'description' in data:
            project.description = data['description']
        if 'technologies' in data:
            project.technologies = data['technologies']
        if 'live_url' in data:
            project.live_url = data['live_url']
        if 'github_url' in data:
            project.github_url = data['github_url']
        if 'featured' in data:
            project.featured = data['featured']
        
        db.session.commit()
        return jsonify(project.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@require_api_key
def delete_project(project_id):
    """Delete a project"""
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== Skills Routes =====

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """Get all skills grouped by category"""
    try:
        skills = Skill.query.order_by(Skill.category, Skill.order).all()
        
        # Group by category
        skills_by_category = {}
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill.to_dict())
        
        return jsonify({
            'skills': skills_by_category,
            'total': len(skills)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/skills/<category>', methods=['GET'])
def get_skills_by_category(category):
    """Get skills by category"""
    try:
        skills = Skill.query.filter_by(category=category).order_by(Skill.order).all()
        return jsonify([skill.to_dict() for skill in skills]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/skills', methods=['POST'])
@require_api_key
def add_skill():
    """Add a new skill"""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['category', 'name']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        skill = Skill(
            category=data['category'],
            name=data['name'],
            proficiency=data.get('proficiency', 70)
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return jsonify(skill.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== Experience Routes =====

@app.route('/api/experiences', methods=['GET'])
def get_experiences():
    """Get all experiences"""
    try:
        experiences = Experience.query.order_by(Experience.order).all()
        return jsonify([exp.to_dict() for exp in experiences]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiences', methods=['POST'])
@require_api_key
def add_experience():
    """Add a new experience"""
    try:
        data = request.get_json()
        
        experience = Experience(
            title=data['title'],
            role=data['role'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
            description=data['description']
        )
        
        db.session.add(experience)
        db.session.commit()
        
        return jsonify(experience.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== Statistics Route =====

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get portfolio statistics"""
    try:
        total_contacts = Contact.query.count()
        unread_contacts = Contact.query.filter_by(is_read=False).count()
        total_projects = Project.query.count()
        total_skills = Skill.query.count()
        total_visitors = Visitor.query.count()
        
        return jsonify({
            'total_contacts': total_contacts,
            'unread_contacts': unread_contacts,
            'total_projects': total_projects,
            'total_skills': total_skills,
            'total_visitors': total_visitors,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== Error Handlers =====

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method not allowed'}), 405


# ===== Before Request Handler =====

@app.before_request
def before_request():
    """Execute before each request"""
    log_visitor()


# ===== Database Initialization =====

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Skill.query.first():
            print("Database already initialized!")
            return
        
        # Add sample skills
        skills = [
            Skill(category='Frontend', name='HTML5', proficiency=90, order=1),
            Skill(category='Frontend', name='CSS3', proficiency=85, order=2),
            Skill(category='Frontend', name='JavaScript', proficiency=80, order=3),
            Skill(category='Backend', name='Python', proficiency=85, order=1),
            Skill(category='Backend', name='Flask', proficiency=80, order=2),
            Skill(category='Backend', name='SQL', proficiency=75, order=3),
            Skill(category='Tools', name='Git & GitHub', proficiency=80, order=1),
            Skill(category='Tools', name='VS Code', proficiency=90, order=2),
        ]
        
        # Add sample projects
        projects = [
            Project(
                title='Personal Portfolio Website',
                description='Responsive portfolio website with HTML, CSS, JavaScript',
                long_description='A complete portfolio website built from scratch with modern web technologies.',
                technologies='HTML5,CSS3,JavaScript',
                featured=True,
                order=1
            ),
            Project(
                title='Task Management App',
                description='Full-stack application with Flask backend and SQLite database',
                technologies='Python,Flask,SQLite',
                featured=True,
                order=2
            ),
        ]
        
        # Add sample experience
        experiences = [
            Experience(
                title='Web Development',
                role='Student Developer',
                start_date=datetime(2023, 1, 1),
                description='Building responsive websites and learning modern frameworks',
                order=1
            ),
            Experience(
                title='Python Programming',
                role='Learner & Practitioner',
                start_date=datetime(2022, 1, 1),
                description='Learning Python fundamentals and backend development',
                order=2
            ),
        ]
        
        db.session.add_all(skills + projects + experiences)
        db.session.commit()
        
        print("✓ Database initialized with sample data!")


if __name__ == '__main__':
    init_db()
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=debug_mode, port=port, host='0.0.0.0')