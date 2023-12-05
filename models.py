from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

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
    name = db.Column(db.String(50), unique=True, nullable=False, primary_key=True)
    sun = db.Column(db.String(10))
    mon = db.Column(db.String(10))
    tue = db.Column(db.String(10))
    wed = db.Column(db.String(10))
    thur = db.Column(db.String(10))
    fri = db.Column(db.String(10))
    sat = db.Column(db.String(10))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    


def get_next_week_schedule():
    today = datetime.now().date()
    next_week_start = today + timedelta(days=(7 - today.weekday()))
    next_week_end = next_week_start + timedelta(days=7)
    
    next_week_schedule = Schedule.query.filter(
        Schedule.date >= next_week_start,
        Schedule.date < next_week_end
    ).all()
    print(next_week_schedule)

    # Process and format the schedule data as needed for display
    formatted_schedule = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
        'Saturday': [],
        'Sunday': [],
    }

    # Iterate through the schedule data and organize it by day and shift
    for entry in next_week_schedule:
        day, shift, user = datetime.strptime(entry.date, '%Y-%m-%d').strftime('%A'), entry.shift, entry.name
        formatted_schedule[day].append([shift, user])
        formatted_schedule[day].sort(key=lambda x: x[0])
    return formatted_schedule

