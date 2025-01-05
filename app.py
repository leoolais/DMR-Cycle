
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, DMR, Operator, CycleOperation, Utilization
from datetime import datetime
import hashlib
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import functools


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Replace with a strong secret key

# Database initialization
engine = create_engine('sqlite:///sterilization_tracker.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Flask-Login Setup
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect to login view if not logged in

class User(UserMixin):
    def __init__(self, id, username, password, first_name, last_name):
        self.id = id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def verify_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest() == self.password

@login_manager.user_loader
def load_user(user_id):
    operator = session.query(Operator).filter(Operator.id == int(user_id)).first()
    if operator:
        return User(operator.id, operator.username, operator.password, operator.first_name, operator.last_name)
    else:
        return None

def login_required_with_error(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You need to log in first!", 'error')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_view

def generate_hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        operator = session.query(Operator).filter(Operator.username == username).first()

        if operator and User(operator.id, operator.username, operator.password, operator.first_name, operator.last_name).verify_password(password):
            user = User(operator.id, operator.username, operator.password, operator.first_name, operator.last_name)
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required_with_error
def index():
    dmrs = session.query(DMR).all()
    return render_template('index.html', dmrs=dmrs)


@app.route('/add_dmr', methods=['GET', 'POST'])
@login_required_with_error
def add_dmr():
    if request.method == 'POST':
        unique_id = request.form['unique_id']
        description = request.form['description']
        brand_model = request.form['brand_model']
        storage_location = request.form['storage_location']

        new_dmr = DMR(
            unique_id=unique_id,
            description=description,
            brand_model=brand_model,
            storage_location=storage_location
        )
        session.add(new_dmr)
        session.commit()
        flash('DMR Added successfully.', 'success')
        return redirect(url_for('index'))
    return render_template('dmr_form.html')

@app.route('/dmr_detail/<int:dmr_id>', methods=['GET'])
@login_required_with_error
def dmr_detail(dmr_id):
    dmr = session.query(DMR).filter(DMR.id == dmr_id).first()
    cycles = session.query(CycleOperation).filter(CycleOperation.dmr_id == dmr_id).all()
    utilizations = session.query(Utilization).filter(Utilization.dmr_id == dmr_id).all()
    return render_template('dmr_detail.html', dmr=dmr, cycles=cycles, utilizations=utilizations)

@app.route('/add_operator', methods=['GET', 'POST'])
@login_required_with_error
def add_operator():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        service_assignment = request.form['service_assignment']

        hashed_password = generate_hash_password(password)

        new_operator = Operator(
            username=username,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            service_assignment=service_assignment
        )
        session.add(new_operator)
        session.commit()
        flash('Operator added successfully.', 'success')
        return redirect(url_for('index'))
    return render_template('operator_form.html')

@app.route('/add_cycle/<int:dmr_id>', methods=['GET', 'POST'])
@login_required_with_error
def add_cycle(dmr_id):
     if request.method == 'POST':
        operation_type = request.form['operation_type']
        location = request.form['location']
        equipment_used = request.form['equipment_used']

        new_cycle = CycleOperation(
            dmr_id=dmr_id,
            operation_type=operation_type,
            operator_id=current_user.id,
            location=location,
            equipment_used=equipment_used
        )

        session.add(new_cycle)
        session.commit()
        flash('Cycle operation logged.', 'success')
        return redirect(url_for('dmr_detail', dmr_id=dmr_id))
     return render_template('cycle_form.html', dmr_id=dmr_id)


@app.route('/add_utilization/<int:dmr_id>', methods=['GET', 'POST'])
@login_required_with_error
def add_utilization(dmr_id):
    if request.method == 'POST':
        intervention_number = request.form['intervention_number']
        healthcare_professional = request.form['healthcare_professional']
        new_utilization = Utilization(
            dmr_id=dmr_id,
            operator_id=current_user.id,
            intervention_number=intervention_number,
            healthcare_professional=healthcare_professional
        )

        session.add(new_utilization)
        session.commit()
        flash('Utilization logged.', 'success')
        return redirect(url_for('dmr_detail', dmr_id=dmr_id))
    return render_template('utilization_form.html', dmr_id=dmr_id)

@app.route('/search', methods=['GET', 'POST'])
@login_required_with_error
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        dmr = session.query(DMR).filter(DMR.unique_id == search_term).first()

        if dmr:
            return redirect(url_for('dmr_detail', dmr_id=dmr.id))
        else:
            flash('No DMR found with this unique ID', 'error')
            return render_template('search.html')

    return render_template('search.html')

@app.route('/profile')
@login_required_with_error
def profile():
    return render_template('profile.html', current_user=current_user)


if __name__ == '__main__':
    app.run(debug=True)