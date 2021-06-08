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
            # lower because discord creates channels in lower case only
            channel_name = event["name"].lower()
            
            if channel_name not in executed_events:
                now = datetime.now()
                event_start_time = interface.to_date_time(event["start"])
                event_end_time = interface.to_date_time(event["end"])

                # compare_start = interface.compare(event_start_time, now)
                # compare_end = interface.compare(event_end_time, now)

                # if compare_start <= 1 and compare_end > 1  and channel_name not in existing_channels:
                if event_start_time <= now and event_end_time > now and channel_name not in existing_channels:
                    await server.create_text_channel(channel_name)
                    executed_events.append(channel_name)
            else:
                now = datetime.now()-timedelta(minutes=1)
                end_time = event["end"]

                if interface.compare(end_time,now) and channel_name in existing_channels:
                    executed_events.remove(channel_name) 
