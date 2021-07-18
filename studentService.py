from datetime import datetime
import interface
import discord

total_subjects = interface.subject_count()


async def get_subject_list_emb(ctx):
    guild = ctx.guild
    # fetching data from mentor sheet
    list_of_all_subjects = interface.get_sheet_list('subject_sheet')

    # initialising an embed
    header_message = "The following courses along with their mentors are given below:"
    emb = discord.Embed(title="Courses Offered", description=header_message)

    serial_no = 1

    # for each mentor
    for i in range(1, len(list_of_all_subjects)):
        value_emb = ''

        # for all the subjects of the mentor
        subject_col = 2
        # split(', '):
        for subject in list_of_all_subjects[i][subject_col].splitlines():
            # add it in the embed and increment the serial no.
            value_emb = value_emb + str(serial_no) + '. ' + subject + "\n"
            serial_no += 1

        # fetching the mentor of the subjects iterated in the previous loop
        mentorobj = await guild.fetch_member(list_of_all_subjects[i][1])
        emb.add_field(name=mentorobj.name, value=value_emb, inline=False)
    return emb


async def enrol_student(ctx, subject_number):
    # check if the input is valid
    if int(subject_number) not in range(1, total_subjects + 1):
        return f"{subject_number} wasn't assigned to any subject"

    #check if the deadline has passed or not
    if not is_before_deadline(subject_number):
        return f"The deadline for the requested subject has already passed!"

    # check if the student had previously enrolled or not
    student_id = ctx.author.id
    student_name = ctx.author.name

    # if the student had already enrolled for the course, inform them.
    if interface.is_present("enrollment", student_id, subject_number):
        return f"{student_name}({ctx.author.discriminator}), Seems like you have already opted for this course"
    
    # role = discord.utils.get(ctx.guild.roles, name=f"{subject_number}")
    # if role == None:
    #     await ctx.guild.create_role(name=f"{subject_number}")
    # role = discord.utils.get(ctx.guild.roles, name=f"{subject_number}")
    # await ctx.author.add_roles(role)
    await add_role(ctx, f"{subject_number}")
    # If not enrolled then enroll them
    interface.insert("enrollment", student_id, subject_number)
    return f"You have been enrolled successfuly :)"


async def add_role(ctx,role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role == None:
        await ctx.guild.create_role(name=role_name)
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    await ctx.author.add_roles(role)

async def remove_role(ctx, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if(role!=None):
        await ctx.author.remove_roles(role)

async def update_student_courses(ctx, fromSubjectNo, ToSubjectNo):
    # check the validity of inputs
    msg = ""
    if int(fromSubjectNo) not in range(1, total_subjects + 1) or int(ToSubjectNo) not in range(1, total_subjects + 1):
        return f"Either one or both of the numbers are not associated with any subject :("

    # check if the deadline has passed or not
    if not is_before_deadline(fromSubjectNo) or not is_before_deadline(ToSubjectNo):
        return f"Deadline for the requested subject(s) has passed!"

    if fromSubjectNo == ToSubjectNo:
        return "Done"

    student_name = ctx.author.name
    student_id = ctx.author.id

    # getting row and column of the student who requested update
    student_col = fromSubjectNo
    student_row = interface.get_row_index(
        "enrollment", student_id, student_col)

    # if students was not enrolled and asked for updation inform them
    if not interface.is_present("enrollment", student_id, fromSubjectNo):
        return f"Hey{student_name},({ctx.author.discriminator})It seems like {fromSubjectNo} was never chosen by you"

    # else remove the student from the old subject and add to the new one
    interface.clear(student_row, student_col)
    await remove_role(ctx, f"{fromSubjectNo}")
    if interface.is_present("enrollment", student_id, ToSubjectNo):
        return f"You have been disenrolled from the course {fromSubjectNo} but you were alerady enrolled in {ToSubjectNo}!"

    interface.insert("enrollment", student_id, ToSubjectNo)
    await add_role(ctx,f"{ToSubjectNo}")
    return f"You have been disenrolled from the course {fromSubjectNo} and you were enrolled in {ToSubjectNo}!"


def is_student_enrolled(student_id, student_col):
    student_row = interface.get_row_index(
        "enrollment", student_id, student_col)
    # if students was not enrolled and asked for updation inform them
    if student_row == -1:
        return False
    return True


def is_before_deadline(subject_num):
    mentor_sheet_list = interface.get_sheet_list('subject_sheet')
    i = 0
    for row in mentor_sheet_list:
        # print(row)
        for subject in row[2].splitlines():
            # print(subject,type(i),type(subject_num))
            if i == int(subject_num):
                now = datetime.today().date()
                deadline = datetime.strptime(row[3],"%d/%m/%Y").date()
                if now < deadline or now == deadline:
                    return True

                return False
            i += 1
    
    return False
