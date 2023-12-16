from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import Availability, db, Schedule, get_next_week_schedule, write_availability_to_database
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
from auth.auth import auth, init_auth_routes
from texts.texts import texts

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'your_secret_key'  # Set a secret key for session management
app.register_blueprint(auth)
app.register_blueprint(texts)

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

@app.route('/test')
def test():
    return 'test passed'

# Route for the login page
@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('auth.login'))

@login_required
@app.route('/availability_form', methods=['GET'])
def availability_form():
    return render_template('availability_form.html')

# TODO: add dates to availabilites so users have to update every week
@login_required
@app.route('/submit_availability', methods=['POST'])
def submit_availability(): 
    if request.method == 'POST':
        name = current_user.username

        def get_selected_values(day):
            return ','.join(request.form.getlist(f'{day}-av[]') if f'{day}-av[]' in request.form else [''])
        
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        avail = {}
        for day in days_of_week:
            avail[day] = get_selected_values(day=day)

        write_availability_to_database(name,avail)

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

        prevEntry =  Schedule.query.filter(Schedule.date.between(next_monday, next_monday+timedelta(days=6))).all()
        for row in prevEntry:
            db.session.delete(row)
        


        for d,day in enumerate(shifts.keys()):
            for availability in availabilities:
                empShifts = request.form.getlist(f"{availability.name}_{day}")
                date = next_monday + timedelta(days=d)
                for shift in empShifts:
                    entry = Schedule(date=date, shift=shift, name=availability.name)
                    db.session.add(entry)
                    print(f'{shift} {day} {availability.name}') 
        
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


