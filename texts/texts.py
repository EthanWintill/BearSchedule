from datetime import datetime, timedelta
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
from twilio import rest
import os
import json
from threading import Thread
from models import Schedule, get_name_from_number, get_number_from_name, get_schedule_for_week, get_staff_without_availability, write_availability_to_database, db
from dotenv import load_dotenv
from models import User

load_dotenv()


texts = Blueprint('texts',__name__)

client = OpenAI()
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_client = rest.Client(account_sid, auth_token)

shift_trade_requests = []

recent_available_shifts = {}

@texts.route('/sms', methods = ['POST'])
def sms():
    message_body = request.form['Body']
    sender_number = int(request.form['From'][-10:]) #cut off country code
    sender_name = get_name_from_number(sender_number)

    if sender_name =='admin':
        manager_incoming_text(message_body, sender_number)
        return 'Manager text recieved', 200  

    intent_json = detect_intent(message_body)

    if intent_json['intent'] != 'update availability':
        resp = MessagingResponse()  
        resp.message(intent_json['coax'])
        return str(resp)

    gpt_resp = parse_availability(message_body)
    reply = gpt_resp_to_str(sender_name, gpt_resp)
        
    resp = MessagingResponse()  
    resp.message(reply)


    return str(resp)

def detect_intent(message_body):
    completion = client.chat.completions.create(
        model='gpt-4o',
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are Intent-Jsonify-bot, you job is to correctly identify if the user wants to update their availabiltiy, ask any question, or do something else. You can only change availabilities, but the user might not know that. Format your response as a JSON object with the key 'intent' and the value as \"update availability\", \"ask question\", or \"other\" If the intent is \"ask question\" or \"other\", you can include a follow up statement answering their question or letting them know you can't do anything but set their availabiltiy with the key \"coax\"}"},
            {"role": "user", "content": "I'm free monday and tuesday after 4, and every other day before 6"},
            {'role': 'assistant', "content": '{"intent":"update availability"}'},
            {'role': 'user', "content": "Why is the sky blue"},
            {'role': 'assistant', "content": '{"intent":"ask question", "coax":"The sky is blue because of Rayleigh scattering, which is the scattering of light off of air molecules. The blue light has a shorter wavelength than other colors, so it is scattered more easily, making the sky appear blue"}'},
            {"role": "user", "content": "Can I get next week's schedule?"},
            {'role': 'assistant', "content": '{"intent":"ask question", "coax":"My bad big dawg, I can only update your availability"}'},
            {"role": "user", "content": "Cancel what I just said!"},
            {'role': 'assistant', "content": '{"intent":"other", "coax":"Sorry homie, I can only update your availability"}'},
            {"role": "user", "content": "What are you?"},
            {'role': 'assistant', "content": '{"intent":"other", "coax":"I am a bot that can only update your availability, so stop asking questions and let me know when you tryna work"}'},
            {"role": "user", "content": "I have open availability"},
            {'role': 'assistant', "content": '{"intent":"update availability"}'},
            {"role": "user", "content": f'{message_body}'}
        ],
    )
    return json.loads(completion.choices[0].message.content)
def parse_availability(message_body):
    completion = client.chat.completions.create(
        model='gpt-4o',
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are Availability-Jsonify-bot, you job is to correctly format my employees work availability into JSON for next week. The JSON object consists of the availability start and end for each day like so: {\"day\": {\"start\": \"time\", \"end\": \"time\"}, ...}. Always use military time. If they say they're free for morning shifts or \"AM\", assume that means they're available 9:00 to 17:30. If they say night, evening, afternoon or PM shifts, assume that means 16:30 to 23:00. Obviously, if they say all day, both, or \"AM,PM\", that means 9:00 to 23:00. If they say they're not free at all for a particular day, store that as {\"day\": {\"start\": \"23:59\", \"end\": \"00:00\"}}. If they don't specify availability for a particular day, assume they are not free that day and store it as {\"day\": {\"start\": \"23:59\", \"end\": \"00:00\"}} The hours of operation are 9:00 to 23:00, keep that in mind as well."},
            {"role": "user", "content": "I'm free monday and tuesday after 4, and every other day before 6"},
            {'role': 'assistant', "content": "{'mon': {'start': '16:00', 'end': '23:59'}, 'tue': {'start': '16:00', 'end': '23:59'}, 'wed': {'start': '09:00', 'end': '18:00'}, 'thu': {'start': '09:00', 'end': '18:00'}, 'fri': {'start': '09:00', 'end': '18:00'}, 'sat': {'start': '09:00', 'end': '18:00'}, 'sun': {'start': '09:00', 'end': '18:00'}}"},
            {"role": "user", "content": "I'm free every evening all week and can work mornings on thursday and friday"},
            {'role': 'assistant', "content": "{'mon': {'start': '16:30', 'end': '23:59'}, 'tue': {'start': '16:30', 'end': '23:59'}, 'wed': {'start': '16:30', 'end': '23:59'}, 'thu': {'start': '09:00', 'end': '23:59'}, 'fri': {'start': '09:00', 'end': '23:59'}, 'sat': {'start': '16:30', 'end': '23:59'}, 'sun': {'start': '16:30', 'end': '23:59'}}"},
            {"role": "user", "content": 'I have open availability'},
            {'role': 'assistant', "content": "{'mon': {'start': '09:00', 'end': '23:59'}, 'tue': {'start': '09:00', 'end': '23:59'}, 'wed': {'start': '09:00', 'end': '23:59'}, 'thu': {'start': '09:00', 'end': '23:59'}, 'fri': {'start': '09:00', 'end': '23:59'}, 'sat': {'start': '09:00', 'end': '23:59'}, 'sun': {'start': '09:00', 'end': '23:59'}}"},            
            {"role": "user", "content": f'{message_body}'},
        ]
    )
    return json.loads(completion.choices[0].message.content)

def gpt_resp_to_str(sender_name, gpt_resp):
    reply = ""
    for day in gpt_resp:
        startTime = datetime.strptime(str(gpt_resp[day]['start']), '%H:%M').strftime('%-I%p')
        endTime = datetime.strptime(str(gpt_resp[day]['end']), '%H:%M').strftime('%-I%p')
        reply += str(day) + '\r\n    Start: ' + startTime + '\r\n    End: ' + endTime + '\r\n'
    reply = reply.replace('\r\n    Start: 11PM\r\n    End: 12AM', ': Not available')
    try:
        write_availability_to_database(sender_name, gpt_resp)
        reply = f'\r\n\r\nUpdated your availability to:\r\n {reply}' #f"{gpt_resp['coax']}" if 'coax' in gpt_resp else 'Availability recieved!'
    except:
        reply = f'Sorry, I had an error, please try rewording you availability\r\n\r\nREFERENCE\r\n {reply}'

    return reply

def manager_incoming_text(message_body, mananger_number):
    if (message_body.upper()) == 'Y' or (message_body.upper()) == 'N':
        approve_or_deny_shift_trade(message_body, mananger_number)

def text_schedule(schedule):
    if os.environ.get('ENV') == 'DEV':
        recipients = User.query.filter(User.username == 'Ethan').with_entities(User.phone, User.username).all()
    else:
        recipients = User.query.filter(User.username != 'admin').with_entities(User.phone, User.username).all()

    for recipient in recipients:
        message_body = 'YOUR SCHEDULE\r\n'
        for day, shiftObjs in schedule.items():
            if recipient[1] not in [shiftObj['name'] for shiftObj in shiftObjs]:
                continue

            recipient_shifts = [shiftObj for shiftObj in shiftObjs if shiftObj['name'] == recipient[1]]
            message_body += f'\r\n-----------{day.upper()}----------\r\n'
            for shiftObj in recipient_shifts:
                message_body+= f'{shiftObj["shift"]}{(7-len(shiftObj["shift"]))*2*" "}{shiftObj["name"]}\r\n'

        message_body += '\r\nGo to https://bearschedule.com/schedule_view to view the full schedule'
        #send message
        try:
            message = twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=message_body, to=recipient[0] )
            print(message.sid)
            # print(f'{recipient[0]}: {message_body}')
        except:
            print(f'{recipient[0]} is not a phone numbers')
            raise Exception('Error sending schedule')
        
        
            

@texts.route('/shift_transfer_request', methods=['POST'])
def shift_transfer_request():
    manager_phone_number = User.query.filter_by(username='admin').first().phone
    data = request.get_json()
    shift_id = data['shift_id']
    name = data['name']
    shiftObj = Schedule.query.filter_by(id=shift_id).first()

    if {'shiftObj':shiftObj, 'name':name} in shift_trade_requests:
        return 'Shift transfer request already sent', 200
    
    shift_trade_requests.append({'shiftObj':shiftObj, 'name':name})
    message_body = f'{name} would like to take {shiftObj.name}\'s {shiftObj.shift} shift on {datetime.strptime(shiftObj.date, "%Y-%m-%d").strftime("%A, %B %-d")} \r\n\r\n Reply with "Y" to approve or "N" to deny.'
    try:
        message = twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=message_body, to=manager_phone_number )
        print(message.sid)
        return 'Shift transfer request sent', 200
    except:
        print(f'error sending message to manager')
        return 'Error sending shift transfer request', 500


def approve_or_deny_shift_trade(message_body, manager_number):
    if os.environ.get('ENV') == 'DEV':
        manager_number = 8329199116

    try:
        shiftObjWithName = shift_trade_requests.pop()
        shiftObj = Schedule.query.filter_by(id = shiftObjWithName['shiftObj'].id).first()
    except:
        twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body='No shift transfer requests to resolve', to=manager_number )
        return 'No shift transfer requests to resolve', 200
    
    oldStaffname = shiftObj.name
    oldStaffNumber = get_number_from_name(oldStaffname)
    newStaffNumber = get_number_from_name(shiftObjWithName['name'])

    if (message_body.upper()) == 'N':
            twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=f'Shift transfer request for {shiftObjWithName["name"]}s {shiftObj.shift} shift has been denied', to=newStaffNumber )
            return 'Shift transfer request denied', 200

    shiftObj.name = shiftObjWithName['name']
    shiftObj.isAvailable = False
    db.session.commit()

    twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=f'Shift transfer request for {oldStaffname}s {shiftObj.shift} shift has been approved', to=newStaffNumber )
    twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=f'Shift transfer request for your {shiftObj.shift} shift has been approved', to=oldStaffNumber )
    return 'Shift transfer request resolved', 200

def send_message(message, phone_number):
    message = twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=message, to=phone_number )

@texts.route('/text-schedule/<week_offset>', methods=['POST'])
def text_schedule_route(week_offset):
    schedule = get_schedule_for_week(int(week_offset))
    try:
        text_schedule(schedule)
        return 'Texted schedule', 200
    except:
        return 'Error texting schedule', 500
    
def alertStaffAvailShift(shiftObj: dict):
    name = shiftObj['name']

    shiftObjStr = str(shiftObj)
    if shiftObjStr in recent_available_shifts:
        if datetime.now() - recent_available_shifts[shiftObjStr] < timedelta(minutes=5):
            return 'Shift already alerted', 200
        else:
            del recent_available_shifts[shiftObjStr]

    recent_available_shifts[shiftObjStr] = datetime.now()

    if os.environ.get('ENV') == 'DEV':
        other_staff = User.query.filter(User.username == 'Ethan').with_entities(User.phone, User.username).all()
    else:
        other_staff = User.query.filter(User.username != name and User.username != 'admin').with_entities(User.phone, User.username).all()

    message_body = f'{name} wants to give away their {shiftObj["shift"]} shift on {datetime.strptime(shiftObj["date"], "%Y-%m-%d").strftime("%A, %B %-d")} \r\n \r\nGo to https://bearschedule.com/schedule_view to take it first it!'
    for staff in other_staff:
        try:
            message = twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=message_body, to=staff[0] )
            print(message.sid)
        except:
            print(f'{staff[0]} is not a phone numbers')
            raise Exception('Error sending schedule')
        

def send_text(staff):
    try:
        message = twilio_client.messages.create(
            from_=os.environ.get('TWILIO_PHONE_NUM'), 
            body=f'Last chance to put in your availability!! If its not entered by saturday morning, I will have to mark you down as open all week!\r\n\r\nYou can reply to this message with next weeks availability or go to https://bearschedule.com/availability_form', 
            to=staff['phone']
        )
        print(message.sid)
    except:
        print(f'{staff["phone"]} is not a phone numbers')
        raise Exception('Error sending schedule')

@texts.route('/availability_alert', methods=['POST'])
def availability_alert():
    if os.environ.get('ENV') == 'DEV':
        lazy_staff = [{'phone': '8329199116'}]*20
    else:
        lazy_staff = get_staff_without_availability()

    for staff in lazy_staff:
        Thread(target=send_text, args=(staff,)).start()

    return 'Availability alert sent', 200

