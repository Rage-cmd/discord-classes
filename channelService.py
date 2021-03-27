from datetime import datetime,timedelta
import interface

present_events = interface.fetch_events(5)

def can_schedule():
    """
    This functions returns a bool depending upon the events that are there 
    in the admin calendar
    """
    global present_events
    return True if present_events else False

async def create_channel(server, executed_events, existing_channels):
    
    if can_schedule():
        global present_events

        for event in present_events:    
            channel_name = event["name"]
            
            if channel_name not in executed_events:
                now = datetime.now()
                event_time = event["start"]
            
                if interface.compare(event_time, now) and channel_name not in existing_channels:
                    await server.create_text_channel(channel_name)
                    executed_events.append(channel_name)
            else:
                now = datetime.now()-timedelta(minutes=1)
                end_time = event["end"]

                if interface.compare(end_time,now) and channel_name in existing_channels:
                    executed_events.remove(channel_name) 
