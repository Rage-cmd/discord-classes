from datetime import datetime,timedelta
from os import TMP_MAX
import interface
import discord

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
    """
    Creates channel(s) by fetching calender events. It will also alert by
    sending a message in the alerts channel.

    Parameters:
        server: The guild in which the channels will be created
        executed_events: list of events that have been executed.
        existing_channels: list of channels present in the guild.
    """
    present_events = fetch_events()
    
    if present_events:
        names= [i["name"] for i in present_events]
        print(names)
        for event in present_events:    
            # lower because discord creates channels in lower case only
            # and spaces are replaced with a hyphen
            channel_name = event["name"].lower().replace(" ","-")

            # if the event hasn't executed yet
            if channel_name not in existing_channels:
                # now = current_time
                now = datetime.now()
                now = now.replace(second=0,microsecond=0) # for ease of comparision

                event_start_time = interface.to_date_time(event["start"])
                event_end_time = interface.to_date_time(event["end"])

                # reminder_time tells when to remind users
                reminder_time = event_start_time - timedelta(minutes=5)

                # if current_time is equal to the reminder_time then send message on 
                # alerts channel
                if now == reminder_time:
                    alert_channel = discord.utils.get(server.text_channels, name = "alerts")
                    await alert_channel.send(channel_name+" is about to start. Get ready.")

                # if the channel hasn't been created yet, create it
                if event_start_time <= now and event_end_time > now:
                    await server.create_text_channel(channel_name)
                    executed_events.append(channel_name)
            else:
                now = datetime.now()
                now = now.replace(second=0, microsecond=0)
                reminder_time = interface.to_date_time(event["end"]) - timedelta(minutes = 2)
                end_time = interface.to_date_time(event["end"]) - timedelta(minutes=1)

                if now == reminder_time:
                    alert_channel = discord.utils.get(server.text_channels, name = "alerts")
                    await alert_channel.send(channel_name+" is about to end.")

                if now == end_time and channel_name in existing_channels:
                    # executed_events.remove(channel_name) 
                    end_channel = discord.utils.get(server.text_channels,name = channel_name)
                    await end_channel.delete()