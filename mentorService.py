import asyncio
import discord
import interface
import datetime
# import bot 
link1 = "https://docs.google.com/forms/d/e/1FAIpQLSfYuSKuXeXy_G5u_-vhaYI9eXXBQk62cBvx1jw2605sf31CQw/viewform"

link2 = "https://docs.google.com/forms/d/e/1FAIpQLSdBxbScZVE91PME2BUVLeAs8cZcoBR2yBzc1tl9ok-fE5PEgQ/viewform"

def get_form_link(arg):
    if arg == 'add_subject':
        return link2
    if arg == 'schedule':
        return link1


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

def subjects_today():
    
    deadlines = interface.get_deadlines()
    today = datetime.datetime.today().date().strftime("%d/%m/%Y")
    
    subjects = []
    subject_ids = []

    if today in deadlines:
        for subject in deadlines[today]:
            subjects.append(subject[0])
            subject_ids.append(subject[1])

    return subjects,subject_ids

async def set_deadline(server,roles,subject_ids):

    in_sheet = interface.get_sheet_list("enrollment")
    for role in roles:
        print(role.name)
    # subjects = [item[0] for item in deadlines[today]]
    # for subject in deadlines[today]:
    #     student_ids = in_sheet.col_values(subject[1])
    #     for student_id in student_ids:
    #         user = await server.fetch_member(int(student_id))
    #         await user.add_roles([role])


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


async def register_mentor(ctx, payload):
    formatstr = f'```!register_mentor "<username>#<tag>"```'
    paylist = payload.split('#')
    if(len(paylist) < 2 or paylist[0]=="" or paylist[1] == ""):
        return f"Wrong Format! Please enter in following format: \n" + formatstr
    username = paylist[0]
    discriminator = paylist[1]
    member =  discord.utils.get(ctx.guild.members, name=username, discriminator=discriminator)
    role = discord.utils.get(ctx.guild.roles, name="Mentor")
    if(member != None):
        await member.add_roles(role)
        return f"Mentor role successfully assigned to {username} #{discriminator}"
    else:
        return f"Some Error Occured, Please check the username and discriminator or try again later! The format is:\n" + formatstr