import interface
import discord

total_subjects = interface.subject_count()


def getlistofallsubjects():
    return interface.get_sheet_list('mentor')


async def getsubjectlistemb(ctx):
    guild = ctx.guild
    # fetching data from mentor sheet
    list_of_all_subjects = getlistofallsubjects()

    # initialising an embed
    header_message = "The following courses along with their mentors are given below:"
    emb = discord.Embed(title="Courses Offered", description=header_message)

    serial_no = 1

    # for each mentor
    for i in range(1, len(list_of_all_subjects)):
        value_emb = ''

        # for each subject of the mentor
        for subject in list_of_all_subjects[i][2].split(', '):
            value_emb = value_emb + str(serial_no) + '. ' + subject + "\n"
            serial_no += 1

        mentorobj = await guild.fetch_member(list_of_all_subjects[i][1])
        emb.add_field(name=mentorobj.name, value=value_emb, inline=False)
    return emb


async def enrolstudent(ctx, subject_number):
    if int(subject_number) not in range(1, total_subjects + 1):
        return f"{subject_number} wasn't assigned to any subject"

        # check if the student had previously enrolled or not
    student_name = ctx.author.name

    if not checkstudentnotenroled(subject_number, student_name):
        return f"{student_name}, Seems like you have already opted for this course"

    # If not enrolled then enroll them
    interface.enrol(student_name, subject_number)
    return f"Thank you, {student_name} you have been enrolled successfuly"


def updatestudentcourses(ctx, fromSubjectNo, ToSubjectNo):
    # check the validity of inputs
    msg = ""
    if int(fromSubjectNo) not in range(1, total_subjects + 1) or int(ToSubjectNo) not in range(1, total_subjects + 1):
        return f"Either one or both of the numbers are not associated with any subject :("

    if fromSubjectNo == ToSubjectNo:
        return "Done"

    user_name = ctx.author.name

    # getting row and column of the student who requested update
    student_col = fromSubjectNo
    student_row = interface.get_row_index(user_name, student_col)

    # if students was not enrolled and asked for updation inform them
    if checkstudentnotenroled(fromSubjectNo, user_name):
        return f"It seems like {fromSubjectNo} was never chosen by you"

    # else remove the student from the old subject and add to the new one
    interface.clear(student_row, student_col)
    if not (checkstudentnotenroled(ToSubjectNo, user_name)):
        return f"You have been disenrolled from the course but you were alerady enrolled in {ToSubjectNo}!"

    interface.enrol(user_name, ToSubjectNo)
    return f"You have been disenrolled from the course and you were enrolled in {ToSubjectNo}!"


def checkstudentnotenroled(student_col, student_name):
    student_row = interface.get_row_index(student_name, student_col)
    # if students was not enrolled and asked for updation inform them
    if student_row == -1:
        return True
    return False
