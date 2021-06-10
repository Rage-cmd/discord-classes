import interface
import discord

total_subjects = interface.subject_count()


def get_list_of_all_subjects():
    return interface.get_sheet_list('mentor')


async def get_subject_list_emb(ctx):
    guild = ctx.guild
    # fetching data from mentor sheet
    list_of_all_subjects = get_list_of_all_subjects()

    # initialising an embed
    header_message = "The following courses along with their mentors are given below:"
    emb = discord.Embed(title="Courses Offered", description=header_message)

    serial_no = 1

    # for each mentor
    for i in range(1, len(list_of_all_subjects)):
        value_emb = ''

        # for all the subjects of the mentor
        subject_col = 2
        for subject in list_of_all_subjects[i][subject_col].splitlines():#split(', '):
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

    # check if the student had previously enrolled or not
    student_id = ctx.author.id
    student_name = ctx.author.name

    # if the student had already enrolled for the course, inform them.
    if is_student_enrolled(student_id,subject_number):
        return f"{student_name}({ctx.author.discriminator}), Seems like you have already opted for this course"

    # If not enrolled then enroll them
    interface.enrol(student_id, subject_number)
    return f"You have been enrolled successfuly :)"


def update_student_courses(ctx, fromSubjectNo, ToSubjectNo):
    # check the validity of inputs
    msg = ""
    if int(fromSubjectNo) not in range(1, total_subjects + 1) or int(ToSubjectNo) not in range(1, total_subjects + 1):
        return f"Either one or both of the numbers are not associated with any subject :("

    if fromSubjectNo == ToSubjectNo:
        return "Done"

    student_name = ctx.author.name
    student_id = ctx.author.id

    # getting row and column of the student who requested update
    student_col = fromSubjectNo
    student_row = interface.get_row_index(student_id, student_col)

    # if students was not enrolled and asked for updation inform them
    if not is_student_enrolled(student_id, fromSubjectNo):
        return f"Hey{student_name},({ctx.author.discriminator})It seems like {fromSubjectNo} was never chosen by you"

    # else remove the student from the old subject and add to the new one
    interface.clear(student_row, student_col)
    if is_student_enrolled(student_id, ToSubjectNo):
        return f"You have been disenrolled from the course {fromSubjectNo} but you were alerady enrolled in {ToSubjectNo}!"

    interface.enrol(student_id, ToSubjectNo)
    return f"You have been disenrolled from the course {fromSubjectNo} and you were enrolled in {ToSubjectNo}!"


def is_student_enrolled(student_id, student_col):
    student_row = interface.get_row_index(student_id, student_col)
    # if students was not enrolled and asked for updation inform them
    if student_row == -1:
        return False
    return True
