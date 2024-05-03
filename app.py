from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import User, db, Schedule, getShifts ,get_schedule_for_week, write_availability_to_database, get_avails_for_week, get_avail_of, get_next_monday, removeShift, addShift, addScheduleShift, removeScheduleShift, setShiftAsAvailableDb
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
from auth.auth import auth, init_auth_routes
from texts.texts import texts, text_schedule


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
    users = [user.username for user in User.query.all()]
    return render_template('availability_form.html', username = current_user.username, names = users)

@login_required
@app.route('/submit_availability', methods=['POST'])
def submit_availability(): 
    if request.method == 'POST':

        if 'avail-for' in request.form:
            name = request.form['avail-for']
        else:
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
@app.route('/removeShift', methods=['DELETE'])
def removeShiftRoute():
    data = request.get_json()
    day, shift, name, offset = data['day'][:3], data['shift'], data['name'], data['offset']
    try:
        removeShift(name, day, shift, offset)
    except Exception as e:
        print(f"Error removing shift: {e}")
        return 'Error! Probably cant find shift', 500
    return '', 204

@login_required
@app.route('/addShift', methods=['POST'])
def addShiftRoute():
    data = request.get_json()
    day, shift, name, offset = data['day'], data['shift'], data['name'], data['offset']
    addShift(name, day ,shift, offset)
    return 'Success', 200

@login_required
@app.route('/newschedule/<week_offset>', methods=['GET','POST'])
@app.route('/newschedule', methods=['GET','POST'])
def new_schedule(week_offset=0):
    week_offset = int(week_offset)+1 #hack to get default to be next week while using utils.modifyRouteParam()
    shifts = getShifts()

    first_monday = get_next_monday()+timedelta(days=week_offset*7-7)
    availabilities = get_avails_for_week(week_offset)

    if request.method=='POST':

        prevEntry =  Schedule.query.filter(Schedule.date.between(first_monday, first_monday+timedelta(days=6))).all()
        for row in prevEntry:
            db.session.delete(row)
        

        #write shifts into db
        for d,day in enumerate(shifts.keys()):
            for availability in availabilities:
                empShifts = request.form.getlist(f"{availability.name}_{day}")
                date = first_monday + timedelta(days=d)
                for shift in empShifts:
                    entry = Schedule(date=date, shift=shift, name=availability.name)
                    db.session.add(entry)
                    print(f'{shift} {day} {availability.name}') 
        
        db.session.commit()

        schedule = get_schedule_for_week(offset=week_offset)
        text_schedule(schedule)

    
    json_availabilities = {avail.name:avail.as_dict() for avail in availabilities}
    return render_template('newschedule.html', availabilities=json_availabilities, days=shifts.keys(), shifts=shifts, week_of=first_monday)

# Route for the schedule_view page
@login_required
@app.route('/schedule_view/<week_offset>')
@app.route('/schedule_view')
def schedule_view(week_offset=0):
    username = current_user.username
    schedule = get_schedule_for_week(int(week_offset))
    user_avail = get_avail_of(current_user.username)
    users = [user.username for user in User.query.all()]

    needed_shifts = getShifts()
    if user_avail:
        del user_avail['week_of']
    else:
        user_avail = {}
    return render_template('schedule_view.html', username=username, schedule=schedule, needed_shifts=needed_shifts ,user_avail=user_avail, names = users, next_monday = get_next_monday()+timedelta(7*int(week_offset)-7))

@app.route('/setShiftAsAvailable', methods=['POST'])
def setShiftAsAvailable():
    data = request.get_json()
    day, shift, name, offset = data['day'], data['shift'], data['name'], data['offset']
    setShiftAsAvailableDb(name, day, shift, offset)
    return '', 204

@app.route('/optimize-schedule', methods=['POST'])
def optimize_schedule():
    data = request.get_json()

    shifts_needed = data.get('shiftsNeeded', {})
    employees_availabilities = data.get('employeesAvailabilities', {})
    print(shifts_needed,employees_availabilities)
    optimal_schedule = perform_optimization(shifts_needed, employees_availabilities)

    return jsonify(optimal_schedule)


def perform_optimization(shifts_needed, staff_availabilities):
    days_of_week = list(shifts_needed.keys())
    schedule = {day: {emp:[] for emp in staff_availabilities} for day in days_of_week}    
    shift_counts = {emp: 0 for emp in staff_availabilities}
    needed_shifts_not_empty = True

    tightest_day = 'mon'
    while len(shifts_needed[tightest_day])==0:
        tightest_day = days_of_week[(days_of_week.index(tightest_day)+1)%7]    
    tightest_shift = shifts_needed[tightest_day][0]

    while(needed_shifts_not_empty):
        for day in days_of_week: 
            for shift in shifts_needed[day]:
                if len(staff_avail_for_shift(day,shift, staff_availabilities))<len(staff_avail_for_shift(tightest_day,tightest_shift, staff_availabilities)):
                    tightest_day, tightest_shift = day, shift

        shift_assignment = min((shift_counts[name], name) for name in staff_avail_for_shift(tightest_day, tightest_shift, staff_availabilities))[1]
        
        shift_counts[shift_assignment]+=1 #update assignments

        #add shift into schedule
        schedule[tightest_day][shift_assignment]+=[tightest_shift]
            

        if tightest_shift[0]=='5': #update availability to reflect shift assignment
            staff_availabilities[shift_assignment][tightest_day]=staff_availabilities[shift_assignment][tightest_day][:-2]
        else:
            staff_availabilities[shift_assignment][tightest_day]=staff_availabilities[shift_assignment][tightest_day][2:]

        shifts_needed[tightest_day].remove(tightest_shift)#update needed shifts
        
        needed_shifts_not_empty = False
        for day in days_of_week: 
            if len(shifts_needed[day])>0:
                tightest_day, tightest_shift = day, shifts_needed[day][0]
                needed_shifts_not_empty = True
                break

    return schedule
    

def staff_avail_for_shift(day, shift, staff_availabilities):
    return [emp for emp in staff_availabilities if checkAvail(shift, emp, day, staff_availabilities)]

def checkAvail(shift, name, day, avails):
    return 'AM' in avails[name][day] and shift[0] != '5' or 'PM' in avails[name][day] and shift[0] == '5'

@app.route('/settings', methods=['GET' , 'POST', 'DELETE'])
def settings():
    if request.method == 'POST':
        data = request.get_json()
        day = data['day']
        shift = data['shift']
        addScheduleShift(day, shift)
    elif request.method == 'DELETE':
        data = request.get_json()
        day = data['day']
        shift = data['shift']
        removeScheduleShift(day, shift)
        
    return render_template('settings.html', needed_shifts = getShifts(), username = current_user.username)

if __name__ == '__main__':
    app.run(debug=True)


