import discord
import os
import requests
import json
import random
from dotenv import load_dotenv
from discord.ext import commands
from tabulate import tabulate
import re

import mentorService
import interface
import calendarService

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!',intents = intents)
total_subjects = interface.subject_count()

#--------------------------------------------------------------
# calendarService.n_events(2)
server = []
#--------------------------------------------------------------
async def get_mentor_name(subject_name):
    mentor_id = interface.get_mentor_id(subject_name)
    mentorobj = await bot.guilds[0].fetch_member( mentor_id )
    return mentorobj.name



@bot.event
async def on_ready():

    global server

    for guild  in bot.guilds:
        print(guild.name)
        if guild.name == "some server":
            server = guild

    print("integ ", server.name)

    print(f'{bot.user.name} is running')


#------------------------------------------------------------------------------------------

from discord.ext import commands, tasks
from datetime import datetime

executed_events = []

@tasks.loop(minutes = 1)
async def create_channels():

    global executed_events
    global server

    running_events = calendarService.n_events(10)
    print(running_events)
    if running_events:
        for event in running_events:
            
            print("FOR",event["name"])
            
            now = datetime.now()
            channel_name = event["name"]

            if channel_name not in executed_events:
                
                print("not")

                if calendarService.compareTime( event["start"], now ) :
                    print("compare")
                    existing_channels = discord.utils.get(server.channels,name = channel_name)
                    
                    if not existing_channels:
                        print("existing")
                        print(f'Creating a new channel: {channel_name}')
                        await server.create_text_channel(channel_name)
                        
                    executed_events.append(channel_name)
            else:
                if calendarService.compareTime(event["end"],now):

                    delete_channel = discord.utils.get(server.channels,name = channel_name)
                    await delete_channel.delete()
                    executed_events.remove(channel_name)

        print(executed_events)    


@create_channels.before_loop
async def before_my_task():
    print("Waiting for the bot to show up...")
    await bot.wait_until_ready()


create_channels.start()

#------------------------------------------------------------------------------------------


# @bot.command(name = 'create-channel')
# @commands.has_role('admin')
# async def create_channel(ctx,channel_name = "general"):
#     guild = ctx.guild
#     print("before all that")
#     existing_channels = discord.utils.get(guild.channels,name = channel_name)
#     if not existing_channels:
#         print(f'Creating a new channel: {channel_name}')
#         await guild.create_text_channel(channel_name)


@bot.command(name = 'create-private-text-channel')
@commands.has_role('moderator')
async def create_private_channel(ctx, channel_name, category, caller_role):
    
    guild = ctx.guild
    role = discord.utils.get(guild.roles,name = caller_role)
    category_need = discord.utils.get(guild.categories, name = category)
    
    for cat in guild.categories:
        print(f'{cat.name}\n')

    if not role:
        await ctx.send(f'Uh oh, there is no role named {caller_role}')
    
    else:
        
        if not category_need:
            await guild.create_category(category)
    
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages = False),
            guild.get_role(role.id) : discord.PermissionOverwrite(read_messages = True),
        }

        required_cat = discord.utils.get(guild.categories, name = category)
        
        print("after overwrites")
        await guild.create_text_channel(channel_name, overwrites = overwrites,category = required_cat)
        print("done creating")


# Sends a message with the list of all subjects along with mentor names
@bot.command(name = 'list')

async def list_subjects(ctx):
    """
        Sends a message with the list of all subjects along with mentor names
    """
    # fetching data from mentor sheet
    list_of_all_subjects = interface.get_sheet_list('mentor')

    # initialising an embed
    header_message = "The following courses along with their mentors are given below:"
    emb = discord.Embed(title = "Courses Offered",description = header_message)

    serial_no = 1

    # for each mentor
    for i in range(1,len(list_of_all_subjects)):
        value_emb = ''
        
        # for each subject of the mentor
        for subject in list_of_all_subjects[i][2].split(', '):
            value_emb = value_emb + str(serial_no) + '. ' + subject + "\n"
            serial_no += 1

        mentorobj = await bot.guilds[0].fetch_member( list_of_all_subjects[i][1])
        emb.add_field(name = mentorobj.name, value = value_emb, inline = False)

    #send the embed message to the channel
    await ctx.send(content = f'Available subjects are\n', embed = emb)
        


@bot.command(name = 'choose')
async def choose_subject(ctx, subject_number): 
    """
        This functions helps students to opt for subjects using the number 
        mentioned against the subject when called the !list command
    """
    # check the validity of input
    if int(subject_number) not in range(1,total_subjects+1):
        await ctx.send(f"{subject_number} wasn't assigned to any subject")
        return
    
    # check if the student had previously enrolled or not
    enrolled_students = interface.enrolled_students(subject_number)
    student_name = ctx.author.name

    if student_name in enrolled_students:
        await ctx.send("You have already opted for this course")
        return

    # If not enrolled then enroll them
    interface.enrol(student_name,subject_number)
    await ctx.send(f"Thank you, {student_name} you have been enrolled successfuly")


@bot.command(name = 'update')
async def update_subject(ctx, fromSubjectNo, ToSubjectNo):
    """
        If a student wants to change their selected subject before the timeline
        then they can do so using the !update command

        Parameters:
            fromSubjectNo: The subject which was currently opted by them
            ToSubjectNo:   The subject which they want to update to
    """

    #check the validity of inputs
    if int(fromSubjectNo) not in range(1,total_subjects+1) or int(ToSubjectNo) not in range(1,total_subjects+1):
        await ctx.send(f"Either one or both of the numbers are not associated with any subject :(")
        return

    if fromSubjectNo == ToSubjectNo:
        await ctx.send("Done!")
        return

    user_name = ctx.author.name

    # getting row and column of the student who requested update
    student_col = fromSubjectNo
    student_row = interface.get_row_index(user_name, student_col)

    # if students was not enrolled and asked for updation inform them
    if student_row == -1:
        await ctx.send(f"It seems like {fromSubjectNo} was never chosen by you")
        return

    # else remove the student from the old subject and add to the new one
    interface.clear(student_row, student_col)
    
    enrolled_students = interface.enrolled_students(ToSubjectNo) 

    if user_name in enrolled_students:
        await ctx.send(f"You have been disenrolled from the course but you were alerady enrolled in {ToSubjectNo}!")
        return

    interface.enrol(user_name,ToSubjectNo)
    await ctx.send(f"You have been disenrolled from the course and you were enrolled in {ToSubjectNo}!")

# @bot.event
# async def on_command_error(ctx,error):
#     if isinstance(error, commands.errors.MissingRole ):
#         await ctx.send("F, you don't have the required permissions.")
#     else:
#         print("Big mistake")

@bot.command(name = "schedule")
async def schedule_link(ctx):
    link  = mentorService.get_form_link()
    await ctx.send(f"Here is the link{link}")

# @bot.command(name = "confirm")
# async def confirm_entry(ctx, name, subject_name):
#     interface

bot.run(TOKEN)

    