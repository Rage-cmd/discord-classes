## Meta 

### v1.0 8th June, 2021

Previously, if the bot started after the start of an event, which has not yet completed, then no channel would have been created. This issue has been fixed now. Channels will be created even when the bot started late or the event was created when the bot was running.

The bot will also notify about the event x minutes before in the alerts channel.

### v1.0.1 9th June, 2021

reminder for the closing of events was also added. Once the event is over, the channel is automatically deleted given that the bot was active when the event ended. (The case where the bot can be inactive can also be handed)