from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
from twilio import rest
import os
import json
from models import get_name_from_number, write_availability_to_database
from dotenv import load_dotenv
from models import User

load_dotenv()


texts = Blueprint('texts',__name__)

client = OpenAI()


@texts.route('/sms', methods = ['POST'])
def sms():
    message_body = request.form['Body']
    sender_number = int(request.form['From'][-10:]) #cut off country code


    completion = client.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are Availability-Jsonify-bot, you job correctly format my employees work availability into JSON for next week. We only have AM and PM shifts. The AM shift is from 10AM-5PM and the PM shift is from 5PM-10PM the correct format looks like this. If they say something like 'I'm free all day' or 'I can work anytime, just assume theat means 'AM,PM'. '{\"monday\":\"AM,PM\",\"tuesday\":\"AM\",....,\"sunday\":\"PM\"}' "}, #\n\nIf the user's response is nonsensical ask it for appropiate clarification with the following format '{\"coax\":\"yourResponseHere\"}'
            {"role": "user", "content": "I'm free monday and tuesday after 4, and every other day before 6"},
            {'role': 'assistant', "content": '{  "monday": "PM", "tuesday": "PM",  "wednesday": "AM",  "thursday": "AM",  "friday": "AM",  "saturday": "AM",  "sunday": "AM"}'},
            {"role": "user", "content": "I'm free every evening all week and can work mornings on thursday and friday"},
            {'role': 'assistant', "content": '{"monday": "PM","tuesday": "PM","wednesday": "PM","thursday": "AM,PM","friday": "AM,PM","saturday": "PM","sunday": "PM"}'},
            {"role": "user", "content": 'I have open availability'},
            {'role': 'assistant', "content": '{  "monday": "AM,PM", "tuesday": "AM,PM",  "wednesday": "AM,PM",  "thursday": "AM,PM",  "friday": "AM,PM",  "saturday": "AM,PM",  "sunday": "AM,PM"}'},
            {"role": "user", "content": f'{message_body}'},
        ]
    )
    gpt_resp = json.loads(completion.choices[0].message.content)
    print(completion.choices)

    sender_name = get_name_from_number(sender_number)

    reply = "\t\n".join([str(day)+' '+str(gpt_resp[day]) for day in gpt_resp])
    try:
        write_availability_to_database(sender_name, gpt_resp)
        reply = f'\n\nUpdated your availability to:\n {reply}' #f"{gpt_resp['coax']}" if 'coax' in gpt_resp else 'Availability recieved!'
    except:
        reply = f'Sorry, I had an error, please try rewording you availability\n\nREFERENCE\n {reply}'
        print(reply)
        
    resp = MessagingResponse()  
    resp.message(reply)


    return str(resp)


def text_schedule(schedule):
    phone_numbers = User.query.with_entities(User.phone).all()
    recipients = ['8329199116'] #[phone[0] for phone in phone_numbers]
    message_body = '-------------------------------\n'
    for day, shifts in schedule.items():
        message_body += f'{day.upper()}\n'
        for shift in shifts:
            message_body+= f'{shift[0]}\t{shift[1]}\n'
        message_body += '-------------------------------\n'
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_client = rest.Client(account_sid, auth_token)
    for number in recipients:
        try:
            message = twilio_client.messages.create( from_=os.environ.get('TWILIO_PHONE_NUM'), body=message_body, to=number )
            print(message.sid)
        except:
            print(f'{number} is not a phone numbers')


