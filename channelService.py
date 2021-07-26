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
async def create_private_channel(ctx, channel_name, category, caller_role):
    print("Creating channel")
    guild = ctx
    role = discord.utils.get(guild.roles, name=caller_role)
    category_need = discord.utils.get(guild.categories, name=category)

    for cat in guild.categories:
        print(f'{cat.name}\n')

    if not role:
        print("returning without creating")
        return

    else:

        if not category_need:
            await guild.create_category(category)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_role(role.id): discord.PermissionOverwrite(read_messages=True),
        }

        required_cat = discord.utils.get(guild.categories, name=category)

        print("after overwrites")
        await guild.create_text_channel(channel_name, overwrites=overwrites, category=required_cat)
        print("done creating")

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
                if reminder_time <= now and event_end_time > now:
                    await create_private_channel(server,channel_name + "-doubt-channel",channel_name,channel_name)
                    await create_private_channel(server,channel_name + "-voice-channel",channel_name,channel_name)
                    await create_private_channel(server,channel_name + "-general-channel",channel_name,channel_name)
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