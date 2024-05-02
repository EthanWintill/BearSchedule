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

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.String(10))
    shift = db.Column(db.String(20))
    name = db.Column(db.String(50))


class Availability(db.Model):
    name = db.Column(db.String(50), nullable=False, primary_key=True)
    week_of = db.Column(db.String(20), nullable=False, primary_key=True)
    sun = db.Column(db.String(10))
    mon = db.Column(db.String(10))
    tue = db.Column(db.String(10))
    wed = db.Column(db.String(10))
    thur = db.Column(db.String(10))
    fri = db.Column(db.String(10))
    sat = db.Column(db.String(10))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

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

def get_schedule_for_week(offset=0):
    week_end = get_next_monday()+timedelta(days=offset*7)
    week_start = week_end+timedelta(days=-7)
    
    next_week_schedule = Schedule.query.filter(
        Schedule.date >= week_start,
        Schedule.date < week_end
    ).all()
    print(next_week_schedule)

    # Process and format the schedule data as needed for display
    formatted_schedule = {}

    # Iterate through the schedule data and organize it by day and shift
    for entry in next_week_schedule:
        day, shift, user = datetime.strptime(entry.date, '%Y-%m-%d').strftime('%a-%d'), entry.shift, entry.name
        formatted_schedule.setdefault(day,[]).append([shift, user])
        formatted_schedule[day].sort(key=lambda x: x[0])
    return formatted_schedule

def write_availability_to_database(name: str, avail: dict):
    next_monday = get_next_monday()
    prevAvail = Availability.query.filter_by(name=name, week_of=next_monday).first()
    if prevAvail:
        # Update existing record
        prevAvail.sun = avail['sunday']
        prevAvail.mon = avail['monday']
        prevAvail.tue = avail['tuesday']
        prevAvail.wed = avail['wednesday']
        prevAvail.thur = avail['thursday']
        prevAvail.fri = avail['friday']
        prevAvail.sat = avail['saturday']
    else:
        # Create a new record
        avail = Availability(
            name=name,
            week_of = next_monday,
            sun=avail['sunday'],
            mon=avail['monday'],
            tue=avail['tuesday'],
            wed=avail['wednesday'],
            thur=avail['thursday'],
            fri=avail['friday'],
            sat=avail['saturday'],
        )
        db.session.add(avail)

    db.session.commit()

def get_name_from_number(number: str):
    record = User.query.filter_by(phone = number).first()
    return None if record is None else str(record.username)

def get_avail_of(name: str):
    next_monday = get_next_monday()
    avail = Availability.query.filter_by(week_of = next_monday, name = name).first()
    print(avail)
    return avail.as_dict() if avail else None
    

def removeShift(name: str, day: str, shift: str):
    this_monday = get_next_monday()-timedelta(days=7)
    entry = Schedule.query.filter_by(name=name, date=this_monday+timedelta(days=['Mon','Tue','Wed','Thur','Fri','Sat','Sun'].index(day)), shift=shift).first()
    db.session.delete(entry)
    db.session.commit()

def addShift(name: str, day: str, shift: str):
    this_monday = get_next_monday()-timedelta(days=7)
    entry = Schedule(date=this_monday+timedelta(days=['mon','tue','wed','thur','fri','sat','sun'].index(day)), shift=shift, name=name)
    db.session.add(entry)
    db.session.commit()