import asyncio
import discord
import interface
import datetime

link = "https://docs.google.com/forms/d/e/1FAIpQLSfYuSKuXeXy_G5u_-vhaYI9eXXBQk62cBvx1jw2605sf31CQw/viewform"


def get_form_link():
    return link


async def ask_info_register(ctx):
    message = """ 
    Enter the following details within 30 seconds to register:
    
        <first_name> <last_name> <email_id>
    
    The bot will ONLY reply if the inputs are valid.
    """
    emb = discord.Embed(title="Registration", description=message)
    await ctx.author.send(embed=emb)

async def ask_info_add(ctx,kind):
    if kind == "subjects":
        message = """
        To add subject(s) reply with the names of the subjects. 

        To enter mulitple subjects, press 'shift + enter' to get a newline 
        inside the text box.
        """
        title = "Add Subjects"
    
    if kind == "date":
        message = """
        Please enter the deadline in the following format:

                        DD/MM/YYYY
        """
        title = "Deadline"

    emb = discord.Embed(title = title, description = message)
    await ctx.author.send(embed = emb)


async def enrol_mentor(ctx, message):

    [first_name, last_name, email] = message.split()
    mentor_id = str(ctx.author.id)

    if interface.is_present("mentors", mentor_id, 4):
        await ctx.author.send("You are already registered!")
    else:
        insert_list = [datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                       first_name,
                       last_name,
                       mentor_id,
                       email]

        interface.insert("mentors", insert_list, 1, many=True)
        await ctx.author.send("Registered Successfully! 😃")

async def add_subject(ctx,subjects,deadline):
    subject_list = subjects.content
    deadline = deadline.content
    timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    mentor_id = str(ctx.author.id)
    insert_list = [timestamp,
                   mentor_id,
                   subject_list,
                   deadline
                  ]
    interface.insert("subject_sheet",insert_list,2,many=True)
    await ctx.author.send("Subject(s) added! 😃")

# needs context

# def check_msg(msg):
#         message = msg.content
#         if not (mentor == msg.author):
#             return False

#         [first_name,last_name,email] = message.split()

#         if not first_name.isalpha() or not last_name.isalpha():
#             return False

#         regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

#         if not re.search(regex,email):
#             return False

#         return True


# #####################
# TO IMPLEMENT: students can not add/update subjects after deadline