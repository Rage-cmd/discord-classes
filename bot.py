import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import interface
import mentorService
import studentService

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
total_subjects = interface.subject_count()


@bot.event
async def on_ready():
    print(f'{bot.user.name} is running')


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
    emb = await studentService.get_subject_list_emb(ctx)
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
    msg = studentService.update_student_courses(ctx, fromSubjectNo,ToSubjectNo)
    await ctx.send(msg)


@bot.command(name="schedule")
async def schedule_link(ctx):
    link = mentorService.get_form_link()
    await ctx.send(f"Here is the link{link}")

bot.run(TOKEN)
