from datetime import datetime,timedelta
import interface

def fetch_events(n=5):
    return interface.fetch_events(n)

# def can_schedule():
#     """
#     This functions returns a bool depending upon the events that are there 
#     in the admin calendar
#     """
#     present_events = fetch_events()
#     return True if present_events else False

async def create_channel(server, executed_events, existing_channels):
    present_events = fetch_events()
    if present_events:
        for event in present_events:    
            # lower because discord creates channels in lower case only
            channel_name = event["name"].lower().replace(" ","-")
            print(channel_name)
            if channel_name not in executed_events:
                now = datetime.now()
                event_start_time = interface.to_date_time(event["start"])
                event_end_time = interface.to_date_time(event["end"])
                print(existing_channels)
                if event_start_time <= now and event_end_time > now and channel_name not in existing_channels:
                    await server.create_text_channel(channel_name)
                    executed_events.append(channel_name)
            else:
                now = datetime.now()-timedelta(minutes=1)
                end_time = event["end"]

                if interface.compare(end_time,now) and channel_name in existing_channels:
                    executed_events.remove(channel_name) 
