from datetime import datetime
import interface

present_events = interface.fetch_events(5)

def can_schedule():
    global present_events
    return True if present_events else False

def add_channel(executed_events, existing_channels):
    global present_events
    upcoming_channels = []

    for event in present_events:    
        channel_name = event["name"]
        
        if channel_name not in executed_events:
            now = datetime.now()
            event_time = event["start"]
        
            if interface.compare(event_time, now) and channel_name not in existing_channels:
                upcoming_channels.append(channel_name)
                executed_events.append(channel_name)
    
    return upcoming_channels
                