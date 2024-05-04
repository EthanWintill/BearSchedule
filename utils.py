from datetime import datetime, timedelta


def get_next_monday():
    today = datetime.now().date()
    return today + timedelta(days=(7 - today.weekday()))