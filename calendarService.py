from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# from datetime 
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


# authorizing the calendar service
def calendar_service():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials2.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

#
service = calendar_service()

def create_event(name):
    event = {
        'summary': name,
        'start':{
            'dateTime':'2021-02-03T15:45:00+05:30',
            # 'timeZone':'Asia/Kolkata'
        },
        'end':{
            'dateTime':'2021-02-03T15:46:00+05:30',
            # 'timeZone':'Asia/Kolkata'
        }
    }

    event = service.events().insert(calendarId = 'primary',body = event).execute()
    print(f"Event created! {event.get('htmlLink')}")


def n_events(n):

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print(f'Getting the upcoming {n} events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=n, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return None

    all_events = []

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime',event['end'].get('date'))

        print( start, end, event['summary'])

        event_info = {
            "name": event['summary'],
            "start": convertTime(start),
            "end": convertTime(end)
        }
        all_events.append(event_info)

    return all_events

def convertTime(time):
    year = int(time[0:4])
    month = int(time[5:7])
    day = int(time[8:10])
    hour = int(time[11:13])
    minute = int(time[14:16])
    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute
    }

def compareTime(time_a,time_b):
    if time_a["day"] == time_b.day and time_a["hour"] == time_b.hour and time_a["minute"] == time_b.minute:
        return 1
    
    if time_a["day"] < time_b.day:
        return 0
    
    if time_a["hour"] < time_b.hour:
        return 0

    if time_a["hour"] < time_b.hour:
        return 0
    
    if time_a["day"] > time_b.day:
        return 2
    
    if time_a["hour"] > time_b.hour:
        return 2

    if time_a["hour"] > time_b.hour:
        return 2

def to_date_time(inp_time):
    return datetime.datetime(
        inp_time["year"],
        inp_time["month"],
        inp_time["day"],
        inp_time["hour"],
        inp_time["minute"]
    )    

# create_event("abc")
# n_events(5)
# print(xyz)