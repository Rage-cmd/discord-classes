import discord 
import interface
import datetime

link = "https://docs.google.com/forms/d/e/1FAIpQLSfYuSKuXeXy_G5u_-vhaYI9eXXBQk62cBvx1jw2605sf31CQw/viewform"

def get_form_link():
    return link

async def ask_info(ctx):
    message = """ 
    Enter the following details within 30 seconds to register:
    
        <first_name> <last_name> <email_id>
    
    The bot will ONLY reply if the inputs are valid.
    """
    emb = discord.Embed(title="Registration", description=message)
    await ctx.author.send(embed=emb)


async def enrol_mentor(ctx,message):

    [first_name,last_name,email] = message.split()
    mentor_id = str(ctx.author.id)

    if interface.is_present("mentors",mentor_id,4):
        await ctx.author.send("You are already registered!")
    else:
        insert_list = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       first_name,
                       last_name,
                       mentor_id,
                       email]
        
        interface.insert("mentors",insert_list,1,many = True)
        await ctx.author.send("Registered Successfully! 😃")

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