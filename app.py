from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import User, Availability, db, Schedule, get_next_week_schedule
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
from auth.auth import auth, init_auth_routes
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'your_secret_key'  # Set a secret key for session management
app.register_blueprint(auth)

login_manager = LoginManager()
login_manager.init_app(app)
init_auth_routes(login_manager)

# Create the database tables
with app.app_context():
    db.init_app(app)
    db.create_all()
    # admin = User(id = 0, username='admin', password_hash=generate_password_hash('adminpassword'), phone = 0)
    # db.session.add(admin)
    # db.session.commit()

# Route for the login page
@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('auth.login'))

@login_required
@app.route('/availability_form', methods=['GET'])
def availability_form():
    return render_template('availability_form.html')

@login_required
@app.route('/submit_availability', methods=['POST'])
def submit_availability(): 
    if request.method == 'POST':
        name = current_user.username
        avail = Availability(name=name, sun=request.form['sunday-av'], mon=request.form['monday-av'], tue=request.form['tuesday-av'], wed=request.form['wednesday-av'], thur=request.form['thursday-av'], fri=request.form['friday-av'], sat=request.form['saturday-av'])
        db.session.add(avail)
        db.session.commit()

    return redirect(url_for('schedule_view')) 

@login_required
@app.route('/newschedule', methods=['GET','POST'])
def new_schedule():
    shifts = {
    'mon': ['10-3H', '5-10H', '10-4', '10-5','5-CL','5-CL','5-CL'],
    'tue': ['10-3H', '5-10H', '10-4', '10-5','5-CL','5-CL','5-CL'],
    'wed': ['10-3H', '5-10H', '10-4', '10-5','5-CL','5-CL','5-CL'],
    'thur': ['10-3H', '5-10H', '10-4', '10-5','5-CL','5-CL','5-CL'],
    'fri': ['10-3H', '5-10H', '10-4', '10-5','5-CL','5-CL','5-CL' ,'5-CL'],
    'sat': ['12-5H', '5-10H','10-5', '10-5', '10-5','5-CL','5-CL','5-CL' ,'5-CL'],
    'sun': ['12-5H', '5-10H','10-5', '10-5', '10-5','5-CL','5-CL','5-CL'],
    }


    availabilities = Availability.query.all()

    if request.method=='POST':

        current_date = datetime.now().date()
        days_until_next_monday = (7 - current_date.weekday()) % 7
        next_monday = current_date + timedelta(days=days_until_next_monday)

        for d,day in enumerate(shifts.keys()):
            for availability in availabilities:
                shift = request.form.get(f"{availability.name}_{day}")
                date = next_monday + timedelta(days=d)
                if shift:
                    entry = Schedule(date=date, shift=shift, name=availability.name)
                    db.session.add(entry)
        
        db.session.commit()     
    
    json_availabilities = {avail.name:avail.as_dict() for avail in availabilities}
    return render_template('newschedule.html', availabilities=json_availabilities, days=shifts.keys(), shifts=shifts)

# Route for the schedule_view page
@login_required
@app.route('/schedule_view')
def schedule_view():
    username = current_user.username
    schedule = get_next_week_schedule()
    return render_template('schedule_view.html', username=username, schedule=schedule)

if __name__ == '__main__':
    app.run(debug=True)


