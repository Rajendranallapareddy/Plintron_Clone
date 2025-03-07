from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    appointments = db.relationship('Appointment', backref='client', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)  # in minutes
    price = db.Column(db.Float)
    appointments = db.relationship('Appointment', backref='service', lazy=True)

class CompanyInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(200))
    about = db.Column(db.Text)
    address = db.Column(db.Text)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    working_hours = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    instagram = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    company_info = CompanyInfo.query.first()
    services = Service.query.all()
    return render_template('index.html', company_info=company_info, services=services)

@app.route('/about')
def about():
    company_info = CompanyInfo.query.first()
    return render_template('about.html', company_info=company_info)

@app.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)

@app.route('/contact')
def contact():
    company_info = CompanyInfo.query.first()
    return render_template('contact.html', company_info=company_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, name=name, phone=phone, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        appointments = Appointment.query.all()
    else:
        appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    
    return render_template('dashboard.html', appointments=appointments)

@app.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    services = Service.query.all()
    
    if request.method == 'POST':
        service_id = request.form.get('service')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        notes = request.form.get('notes')
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        appointment = Appointment(
            user_id=current_user.id,
            service_id=service_id,
            date=date_obj,
            time=time_obj,
            notes=notes
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('book_appointment.html', services=services)

@app.route('/admin/appointments')
@login_required
def admin_appointments():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    appointments = Appointment.query.all()
    return render_template('admin/appointments.html', appointments=appointments)

@app.route('/admin/services', methods=['GET', 'POST'])
@login_required
def admin_services():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        duration = request.form.get('duration')
        price = request.form.get('price')
        
        service = Service(name=name, description=description, duration=duration, price=price)
        db.session.add(service)
        db.session.commit()
        
        flash('Service added successfully!', 'success')
        return redirect(url_for('admin_services'))
    
    services = Service.query.all()
    return render_template('admin/services.html', services=services)

@app.route('/admin/company-info', methods=['GET', 'POST'])
@login_required
def admin_company_info():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    company_info = CompanyInfo.query.first()
    
    if request.method == 'POST':
        if not company_info:
            company_info = CompanyInfo()
        
        company_info.name = request.form.get('name')
        company_info.tagline = request.form.get('tagline')
        company_info.about = request.form.get('about')
        company_info.address = request.form.get('address')
        company_info.email = request.form.get('email')
        company_info.phone = request.form.get('phone')
        company_info.working_hours = request.form.get('working_hours')
        company_info.facebook = request.form.get('facebook')
        company_info.twitter = request.form.get('twitter')
        company_info.linkedin = request.form.get('linkedin')
        company_info.instagram = request.form.get('instagram')
        
        if not company_info.id:
            db.session.add(company_info)
        
        db.session.commit()
        
        flash('Company information updated successfully!', 'success')
        return redirect(url_for('admin_company_info'))
    
    return render_template('admin/company_info.html', company_info=company_info)

@app.route('/api/update-appointment-status', methods=['POST'])
@login_required
def update_appointment_status():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    appointment_id = request.json.get('appointment_id')
    status = request.json.get('status')
    
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404
    
    appointment.status = status
    db.session.commit()
    
    return jsonify({'success': True})

# Initialize the database
with app.app_context():
    try:
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@plintron.com').first()
        if not admin:
            admin = User(
                email='admin@plintron.com',
                name='Admin',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            
            # Add default company info
            company_info = CompanyInfo(
                name='Plintron Technical Solutions',
                tagline='Innovative Technical Solutions for Your Business',
                about='Plintron Technical Solutions is a leading provider of technical services and solutions for businesses of all sizes.',
                address='123 Tech Street, Silicon Valley, CA 94043',
                email='info@plintron.com',
                phone='+1 (555) 123-4567',
                working_hours='Monday-Friday: 9:00 AM - 6:00 PM',
                facebook='https://facebook.com/plintron',
                twitter='https://twitter.com/plintron',
                linkedin='https://linkedin.com/company/plintron',
                instagram='https://instagram.com/plintron'
            )
            db.session.add(company_info)
            
            # Add default services
            services = [
                Service(name='IT Consulting', description='Expert IT consulting services for your business needs.', duration=60, price=150.00),
                Service(name='Network Setup', description='Professional network setup and configuration.', duration=120, price=250.00),
                Service(name='Software Development', description='Custom software development tailored to your requirements.', duration=180, price=350.00),
                Service(name='Cloud Migration', description='Seamless migration of your systems to the cloud.', duration=240, price=450.00)
            ]
            db.session.add_all(services)
            
            db.session.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == '__main__':
    app.run(debug=True)