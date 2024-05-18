from datetime import datetime
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
from twilio import rest
import os
import json
from models import Schedule, get_name_from_number, get_number_from_name, get_schedule_for_week, write_availability_to_database, db
from dotenv import load_dotenv
from models import User

load_dotenv()


texts = Blueprint('texts',__name__)

client = OpenAI()
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_client = rest.Client(account_sid, auth_token)

shift_trade_requests = []

@texts.route('/sms', methods = ['POST'])
def sms():
    message_body = request.form['Body']
    sender_number = int(request.form['From'][-10:]) #cut off country code
    sender_name = get_name_from_number(sender_number)

    if sender_name =='admin' and ((message_body.upper()) == 'Y' or (message_body.upper()) == 'N'):
        approve_or_deny_shift_trade(message_body, sender_number)
        return 'Shift transfer request resolved', 200
        


    completion = client.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are Availability-Jsonify-bot, you job is to correctly format my employees work availability into JSON for next week. The JSON object consists of the availability start and end for each day like so: {\"day\": {\"start\": \"time\", \"end\": \"time\"}, ...}. Always use military time. If they say they're free for morning shifts or \"AM\", assume that means they're available 9:00 to 17:30. If they say night, evening, afternoon or PM shifts, assume that means 16:30 to 23:00. Obviously, if they say all day, both, or \"AM,PM\", that means 9:00 to 23:00. If they say they're not free at all for a particular day, store that as {\"day\": {\"start\": \"23:59\", \"end\": \"00:00\"}}. If they don't specify availability for a particular day, assume they are not free that day and store it as {\"day\": {\"start\": \"23:59\", \"end\": \"00:00\"}}"}, #\n\nIf the user's response is nonsensical ask it for appropiate clarification with the following format '{\"coax\":\"yourResponseHere\"}' format '{\"coax\":\"yourResponseHere\"}'
            {"role": "user", "content": "I'm free monday and tuesday after 4, and every other day before 6"},
            {'role': 'assistant', "content": "{'mon': {'start': '16:00', 'end': '23:59'}, 'tue': {'start': '16:00', 'end': '23:59'}, 'wed': {'start': '09:00', 'end': '18:00'}, 'thu': {'start': '09:00', 'end': '18:00'}, 'fri': {'start': '09:00', 'end': '18:00'}, 'sat': {'start': '09:00', 'end': '18:00'}, 'sun': {'start': '09:00', 'end': '18:00'}}"},
            {"role": "user", "content": "I'm free every evening all week and can work mornings on thursday and friday"},
            {'role': 'assistant', "content": "{'mon': {'start': '16:30', 'end': '23:59'}, 'tue': {'start': '16:30', 'end': '23:59'}, 'wed': {'start': '16:30', 'end': '23:59'}, 'thu': {'start': '09:00', 'end': '23:59'}, 'fri': {'start': '09:00', 'end': '23:59'}, 'sat': {'start': '16:30', 'end': '23:59'}, 'sun': {'start': '16:30', 'end': '23:59'}}"},
            {"role": "user", "content": 'I have open availability'},
            {'role': 'assistant', "content": "{'mon': {'start': '09:00', 'end': '23:59'}, 'tue': {'start': '09:00', 'end': '23:59'}, 'wed': {'start': '09:00', 'end': '23:59'}, 'thu': {'start': '09:00', 'end': '23:59'}, 'fri': {'start': '09:00', 'end': '23:59'}, 'sat': {'start': '09:00', 'end': '23:59'}, 'sun': {'start': '09:00', 'end': '23:59'}}"},            
            {"role": "user", "content": f'{message_body}'},
        ]
    )
    gpt_resp = json.loads(completion.choices[0].message.content)
    print(completion.choices)


    reply = ""
    for day in gpt_resp:
        startTime = datetime.strptime(str(gpt_resp[day]['start']), '%H:%M').strftime('%-I%p')
        endTime = datetime.strptime(str(gpt_resp[day]['end']), '%H:%M').strftime('%-I%p')
        reply += str(day) + '\n    Start: ' + startTime + '\n    End: ' + endTime + '\n'
    reply = reply.replace('\n    Start: 11PM\n    End: 12AM', ': Not available')
    print(reply)
    try:
        write_availability_to_database(sender_name, gpt_resp)
        reply = f'\n\nUpdated your availability to:\n {reply}' #f"{gpt_resp['coax']}" if 'coax' in gpt_resp else 'Availability recieved!'
    except:
        reply = f'Sorry, I had an error, please try rewording you availability\n\nREFERENCE\n {reply}'
        print(reply)
        
    resp = MessagingResponse()  
    resp.message(reply)


    return str(resp)

@texts.route('/text-schedule', methods=['POST'])
def text_schedule_route():
    schedule = get_schedule_for_week(1)
    try:
        text_schedule(schedule)
        return 'Texted schedule', 200
    except:
        return 'Error texting schedule', 500

def text_schedule(schedule):
    phone_numbers = User.query.with_entities(User.phone).all()
    recipients = [phone[0] for phone in phone_numbers]
    message_body = 'SCHEDULE\n'
    for day, shiftObjs in schedule.items():
        message_body += f'\n-----------{day.upper()}----------\n'
        for shiftObj in shiftObjs:
            message_body+= f'{shiftObj["shift"]}\t{shiftObj["name"]}\n'

    message_body += f'-------------------------------'
        
    for number in recipients:
        try:
            message = twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=message_body, to=number )
            print(message.sid)
        except:
            print(f'{number} is not a phone numbers')
            raise Exception('Error sending schedule')
            

@texts.route('/shift_transfer_request', methods=['POST'])
def shift_transfer_request():
    manager_phone_number = User.query.filter_by(username='admin').first().phone
    data = request.get_json()
    shift_id = data['shift_id']
    name = data['name']
    shiftObj = Schedule.query.filter_by(id=shift_id).first()
    shift_trade_requests.append({'shiftObj':shiftObj, 'name':name})
    message_body = f'{name} would like to take {shiftObj.name}\'s {shiftObj.shift} shift on {datetime.strptime(shiftObj.date, "%Y-%m-%d").strftime("%A, %B %-d")} '
    try:
        message = twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=message_body, to=manager_phone_number )
        print(message.sid)
        return 'Shift transfer request sent', 200
    except:
        print(f'error sending message to manager')
        return 'Error sending shift transfer request', 500


def approve_or_deny_shift_trade(message_body, manager_number):
    
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
