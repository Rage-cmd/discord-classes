from calendarService import calendar_service
import os

import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv
from datetime import datetime
import re 
import asyncio

import interface
import mentorService
import studentService
import channelService
import copy

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
total_subjects = interface.subject_count()

server_name = "some server"
server = []
executed_events = []


def channel_names(channel_list):
    """
    A utility function to get the names of all the channels in the server.
    Parameters:
        List of channels
    Returns:
        List of string (names of the channels)
    """
    names = []
    for channel in channel_list:
        names.append(channel.name)
    return names


# async def create_roles(server,all_subject_list):
#     subject_col = 2
#     for i in range(1,len(all_subject_list)):
#         for subject in all_subject_list[i][subject_col].splitlines():#.split(', '):
#             roles = await server.fetch_roles()
            
#             if not discord.utils.get(roles,name = subject):
#                 await server.create_role(name = subject, mentionable = True)

async def create_roles(server,subjects):
    created_roles = []
    for subject in subjects:
        roles = await server.fetch_roles()
        if not discord.utils.get(roles,name = subject):
            role  = await server.create_role(name = subject, mentionable = True)
            created_roles.append(role)
    
    return created_roles
        

async def createRole(guild, role_name):
    role = guild.get(guild.roles, name=role_name)
    if(role==None):
        await guild.create_role(name=role_name)

#capture the server(global variable) when the bot gets ready
@bot.event
async def on_ready():
    global server
    
    for guild in bot.guilds:
        if guild.name == server_name:
            server = guild
            break

    # roles = await server.fetch_roles()
    # for role in roles:
    #     print(role.name)
    #     if role.name != "philbert" and role.name != "@everyone" and role.name != "Interaction":
    #         await role.delete()

    check_deadlines.start()
    udpate_EnrollmentSheet.start()

    print(f'{bot.user.name} is running')
    await createRole(server,"Mentor")



# The asynchronous fucntion create_channels will run every minute
@tasks.loop(minutes = 1)
async def create_channels():
    """
    This function will look for any events in the admin calendar at the current time
    and will create channels accordingly.
    """
    global executed_events
    global server
    print("running...")
    existing_channels = channel_names(server.channels)

    await channelService.create_channel(server, executed_events, existing_channels)

@tasks.loop(minutes=1)
async def udpate_EnrollmentSheet():
    interface.update_enrollment_sheet("enrollment")

@tasks.loop(seconds = 15)
async def check_deadlines():
    global server
    subjects, subject_ids = mentorService.subjects_today()
    if subjects:
        roles = await create_roles(server,subjects)
        await mentorService.set_deadline(server,roles,subject_ids)


# the loop should start only after the bot is set up
@create_channels.before_loop
async def before_my_task():
    print("Waiting for the bot to show up...")
    await bot.wait_until_ready()

create_channels.start()

# at this point we are sure that the bot is ready

@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name="general"):
    guild = ctx.guild
    print("before all that")
    existing_channels = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channels:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.command(name='create-private-text-channel')
@commands.has_role('moderator')
async def create_private_channel(ctx, channel_name, category, caller_role):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=caller_role)
    category_need = discord.utils.get(guild.categories, name=category)

    for cat in guild.categories:
        print(f'{cat.name}\n')

    if not role:
        await ctx.send(f'Uh oh, there is no role named {caller_role}')

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


# Sends a message with the list of all subjects along with mentor names
@bot.command(name='list')
async def list_subjects(ctx):
    """
        Sends a message with the list of all subjects along with mentor names
    """
    message = await studentService.get_subject_list_emb(ctx)
    emb = discord.Embed(title = 'The following are the upcoming courses along with their mentors and the deadline for registration\n', description = message)
    await ctx.send(content=f'Available subjects are\n', embed=emb)


@bot.command(name='choose')
async def choose_subject(ctx, subject_number):
    """
        This functions helps students to opt for subjects using the number
        mentioned against the subject when called the !list command
    """
    msg = await studentService.enrol_student(ctx, subject_number)
    await ctx.send(msg)


@bot.command(name='update')
async def update_subject(ctx, fromSubjectNo, ToSubjectNo):
    """
        If a student wants to change their selected subject before the timeline
        then they can do so using the !update command

        Parameters:
            fromSubjectNo: The subject which was currently opted by them
            ToSubjectNo:   The subject which they want to update to
    """
    msg = await studentService.update_student_courses(ctx, fromSubjectNo,ToSubjectNo)
    await ctx.send(msg)


@bot.command(name="schedule")
async def schedule_link(ctx):
    """
        Will return a link for the form that can help mentors 
        schedule lectures
    """

    link = mentorService.get_form_link()
    await ctx.send(f"Here is the link{link}")

@bot.command(name="did")
async def get_discord_id(ctx):
    """
        This command will reply the author with 
        their discord ID,
    """
    mentor = ctx.author
    list_wb = await ctx.guild.webhooks()
    webh = list_wb[0]
    await mentor.send(f"Your discord ID is {str(mentor.id)}")

@bot.command(name = "register")
async def register(ctx):
    """
        This command can be used by a mentor to register themselves.
        The bot will ask the mentor to reply with their details.
    """
    mentor = ctx.author
    await mentorService.ask_info_register(ctx)

    # to make sure that the message was sent by the mentor and 
    # the inputs are valid
    def check_msg(msg):
        message = msg.content
        if not (mentor == msg.author):
            return False
        
        [first_name,last_name,email] = message.split()

        if not first_name.isalpha() or not last_name.isalpha():
            return False
        
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

        if not re.search(regex,email):
            return False
        
        return True

    try:
        # if inputs are valid then register the mentor or inform them if registered already
        message = await bot.wait_for("message",check = check_msg, timeout=20)
        if message:
            msg = await mentorService.enrol_mentor(ctx,message.content)

    except asyncio.TimeoutError:
        # if the mentor fails to reply in the given time limit then inform them so
        await mentor.send("Sorry, you didn't reply in time ⏲️!")

@bot.command(name = 'add')
async def add_subject(ctx):
    mentor = ctx.author
    await mentorService.ask_info_add(ctx,"subjects")

    def check_sub(msg):
        message = msg.content
        if not (mentor == msg.author):
            return False
        
        subjects = message.splitlines()
        
        if not subjects:
            return False
        return True 
    
    def check_date(msg):
        message = msg.content
        if not mentor == msg.author:
            return False
        day, month ,year = message.split('/')
        
        return interface.is_valid_date(int(day),int(month),int(year))

    subjects = await bot.wait_for("message",check = check_sub)
    if subjects:
        await mentorService.ask_info_add(ctx,"date")
        deadline = await bot.wait_for("message",check = check_date)
        if deadline:
            await mentorService.add_subject(ctx,subjects,deadline)

@bot.command(name='register_mentor')
@commands.has_role('admin')
async def registerMentor(ctx, payload=""):
    await ctx.send(await mentorService.register_mentor(ctx,payload))
bot.run(TOKEN)
