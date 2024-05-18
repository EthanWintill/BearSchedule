import json
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from utils import get_next_monday

db = SQLAlchemy()


# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.Integer, unique=True)
    def as_dict(self):
       return {'id': self.id, 'username': self.username, 'phone': self.phone}

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.String(10))
    shift = db.Column(db.String(20))
    name = db.Column(db.String(50))
    isAvailable = db.Column(db.Boolean, default=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    shift_ref = db.relationship('Shift', backref='schedule')
    startTime = db.Column(db.String(10))
    endTime = db.Column(db.String(10))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Availability(db.Model):
    name = db.Column(db.String(50), nullable=False, primary_key=True)
    week_of = db.Column(db.String(20), nullable=False, primary_key=True)
    sun_start = db.Column(db.String(10))
    sun_end = db.Column(db.String(10))
    mon_start = db.Column(db.String(10))
    mon_end = db.Column(db.String(10))
    tue_start = db.Column(db.String(10))
    tue_end = db.Column(db.String(10))
    wed_start = db.Column(db.String(10))
    wed_end = db.Column(db.String(10))
    thu_start = db.Column(db.String(10))
    thu_end = db.Column(db.String(10))
    fri_start = db.Column(db.String(10))
    fri_end = db.Column(db.String(10))
    sat_start = db.Column(db.String(10))
    sat_end = db.Column(db.String(10))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day = db.Column(db.String(10))
    shift = db.Column(db.String(20))
    startTime = db.Column(db.String(10))
    endTime = db.Column(db.String(10))
    type = db.Column(db.String(10))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def addScheduleShift(day, shift, start, end, shift_type):
    entry = Shift(day=day, shift=shift, startTime=start, endTime=end, type=shift_type)
    db.session.add(entry)
    db.session.commit()

def removeScheduleShift(day, shift):
    entry = Shift.query.filter_by(day=day, shift=shift).first()
    db.session.delete(entry)
    db.session.commit()

def getShifts():
    shifts = Shift.query.all()
    # Organize shifts by day
    shifts = {day: sorted([shift.as_dict() for shift in shifts if shift.day == day], key=lambda x: x['startTime']) for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']}

    return shifts


#Availability
def get_next_week_availabilites():
    next_week_start = get_next_monday()
    
    next_week_avails = Availability.query.filter(
        Availability.week_of == next_week_start).all()
    return next_week_avails

def get_avails_for_week(week_offset=0):
    week_start = get_next_monday()+timedelta(days=week_offset*7-7)
    week_avails = Availability.query.filter(
        Availability.week_of == week_start).all()    
    return week_avails


# Takes availabilty dictionary in the form of: avail{ name: {day: {start: time, end: time}} and name of the employee
def write_availability_to_database(name: str, avail: dict):
    next_monday = get_next_monday()
    prevAvail = Availability.query.filter_by(name=name, week_of=next_monday).first()
    if prevAvail:
        # Update existing record
        prevAvail.sun_start = avail['sun']['start']
        prevAvail.sun_end = avail['sun']['end']
        prevAvail.mon_start = avail['mon']['start']
        prevAvail.mon_end = avail['mon']['end']
        prevAvail.tue_start = avail['tue']['start']
        prevAvail.tue_end = avail['tue']['end']
        prevAvail.wed_start = avail['wed']['start']
        prevAvail.wed_end = avail['wed']['end']
        prevAvail.thu_start = avail['thu']['start']
        prevAvail.thu_end = avail['thu']['end']
        prevAvail.fri_start = avail['fri']['start']
        prevAvail.fri_end = avail['fri']['end']
        prevAvail.sat_start = avail['sat']['start']
        prevAvail.sat_end = avail['sat']['end']
    else:
        # Create a new record
        avail = Availability(
            name=name,
            week_of=next_monday,
            sun_start=avail['sun']['start'],
            sun_end=avail['sun']['end'],
            mon_start=avail['mon']['start'],
            mon_end=avail['mon']['end'],
            tue_start=avail['tue']['start'],
            tue_end=avail['tue']['end'],
            wed_start=avail['wed']['start'],
            wed_end=avail['wed']['end'],
            thu_start=avail['thu']['start'],
            thu_end=avail['thu']['end'],
            fri_start=avail['fri']['start'],
            fri_end=avail['fri']['end'],
            sat_start=avail['sat']['start'],
            sat_end=avail['sat']['end'],
        )
        db.session.add(avail)

    db.session.commit()


def get_avail_of(name: str):
    next_monday = get_next_monday()
    avail = Availability.query.filter_by(week_of = next_monday, name = name).first()
    #format data as {day: {start: time, end: time}}
    if avail is None:
        return {}
    fomatted_avail = {day: {'start': getattr(avail, f'{day}_start'), 'end': getattr(avail, f'{day}_end')} for day in ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']}
    return fomatted_avail    

#schedule
def get_schedule_for_week(offset=0):
    week_end = get_next_monday()+timedelta(days=offset*7)
    week_start = week_end+timedelta(days=-7)
    
    next_week_schedule = Schedule.query.filter(
        Schedule.date >= week_start,
        Schedule.date < week_end
    ).all()
    next_week_dates = [week_start+timedelta(days=i) for i in range(7)]
    # Process and format the schedule data as needed for display
    formatted_schedule = {date.strftime('%a-%d'): [] for date in next_week_dates }
    print(formatted_schedule)
    # Iterate through the schedule data and organize it by day and shift
    for entry in next_week_schedule:
        day = datetime.strptime(entry.date, '%Y-%m-%d').strftime('%a-%d')
        formatted_schedule.setdefault(day,[]).append(entry.as_dict())
        formatted_schedule[day].sort(key=lambda x: x['shift'])
    return formatted_schedule


def removeShift(name: str, day: str, shift: str, week_offset=0):
    entry = getScheduleEntry(name, day, shift, week_offset)
    db.session.delete(entry)
    db.session.commit()

def addShift(name: str, day: str, shift_id: int, week_offset=0):
    this_monday = get_next_monday()+timedelta(days=week_offset*7-7)
    relevant_shift = Shift.query.filter_by(id=shift_id).first()
    entry = Schedule(date=this_monday+timedelta(days=['mon','tue','wed','thu','fri','sat','sun'].index(day)), shift=relevant_shift.shift, name=name, shift_id=shift_id, startTime=relevant_shift.startTime, endTime=relevant_shift.endTime)
    db.session.add(entry)
    db.session.commit()

def toggleShiftAvailabilityDB(name: str, day: str, shift: str, week_offset=0):
    entry = getScheduleEntry(name, day, shift, week_offset)
    entry.isAvailable = not entry.isAvailable
    db.session.commit()


def getScheduleEntry(name: str, day: str, shift: str, week_offset=0):
    this_monday = get_next_monday()+timedelta(days=week_offset*7-7)
    entry = Schedule.query.filter_by(name=name, date=this_monday+timedelta(days=['mon','tue','wed','thu','fri','sat','sun'].index(day)), shift=shift).first()
    return entry


#User
def get_name_from_number(number: str):
    record = User.query.filter_by(phone = number).first()
    return None if record is None else str(record.username)

def get_number_from_name(name: str):
    record = User.query.filter_by(username = name).first()
    return None if record is None else str(record.phone)

def update_password(id: int, password: str):
    record = User.query.filter_by(id = id).first()
    record.password_hash = generate_password_hash(password)
    db.session.commit()

def delete_user(id: int):
    user = User.query.filter_by(id = id).first()

    #delete availabilities for this week
    next_monday = get_next_monday()
    prevAvail = Availability.query.filter_by(name=user.username, week_of=next_monday).first()
    if prevAvail:
        db.session.delete(prevAvail)
        
    db.session.delete(user)
    db.session.commit()
