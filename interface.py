import gspread
from gspread.models import Worksheet
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import re
import math
import calendarService

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Responses')

mentor_sheet = sheet.get_worksheet(0)
student_sheet = sheet.get_worksheet(1)
course_sheet = sheet.get_worksheet(2)
schedule_sheet = sheet.get_worksheet(3)

# testing-sheet
test_sheet = sheet.get_worksheet(4)


def pretty_sheet():
    """
    Experimental function, not to be called yet.
    """
    col_id = 2
    col_id_sub = 3
    n_rows = test_sheet.row_count

    test_sheet.sort((col_id, 'asc'))
    column_val_id = test_sheet.col_values(col_id)
    column_val_sub = test_sheet.col_values(col_id_sub)

    i = 0
    while i < len(column_val_id)-1:
        cell_v1 = column_val_id[i]
        cell_v2 = column_val_id[i+1]

        start_id = gspread.utils.rowcol_to_a1(i+1, col_id)
        start_sub = gspread.utils.rowcol_to_a1(i+1, col_id_sub)

        i_sub = i+1
        append_sub = column_val_sub[i]

        if cell_v1 == cell_v2:

            while cell_v1 == cell_v2:
                i += 1
                cell_v2 = column_val_id[i+1]
                append_sub += "\n" + column_val_sub[i]
                # print(column_val_sub[i])

            end_id = gspread.utils.rowcol_to_a1(i+1, col_id)
            end_sub = gspread.utils.rowcol_to_a1(i+1, col_id_sub)

            merge_range_id = start_id + ":" + end_id
            merge_range_sub = start_sub + ":" + end_sub

            test_sheet.merge_cells(merge_range_id, merge_type="MERGE_COLUMNS")
            test_sheet.merge_cells(merge_range_sub, merge_type="MERGE_COLUMNS")

            test_sheet.update_cell(i_sub, col_id_sub, append_sub)

        i += 1


def create_enrollment_sheet(name):
    """
    Once the mentors have submitted the subjects/topics they will be
    mentoring, this function will create, if already not created,
    another worksheet with column headers as the subjects given. 

    Parameters: 
        name: (string) The name of the worksheet
    
    Returns:
        worksheet object
    """
    try:
        enrol_sheet = sheet.worksheet(name)
    except:
        enrol_sheet = sheet.add_worksheet(name, rows=100, cols=50)
        subject_list_mentor = mentor_sheet.col_values(3)[1:]

        subject_list = []
        for subjects in subject_list_mentor:
            for subject in subjects.splitlines():
                subject_list.append(subject)

        # header_size = len(subject_list)
        # start_header = gspread.utils.rowcol_to_a1(1,1)
        # end_header = gspread.utils.rowcol_to_a1(1,header_size)

        # header_range = start_header + ":" + end_header
        enrol_sheet.update([subject_list])


def subject_count():
    return len(course_sheet.row_values(1))


def enrol(student_id, subject_number):
    row = next_row(course_sheet, subject_number)
    course_sheet.update_cell(row, subject_number, str(student_id))


def enrolled_students(subject_number):
    return course_sheet.col_values(subject_number)


def get_sheet_list(query):
    if query == 'mentor':
        return mentor_sheet.get_all_values()
    else:
        return student_sheet.get_all_values()


def get_row_index(query, column):
    col_elements = course_sheet.col_values(column)
    if str(query) not in col_elements:
        return -1
    return col_elements.index(str(query))+1


def clear(row, column):
    del_range = course_sheet.range(row, column, row, column)
    del_range[0].value = ''
    course_sheet.update_cells(del_range, value_input_option='USER_ENTERED')


def cell_value(row, col):
    return course_sheet.cell(row, col).value


def get_mentor_id(subject_name):
    subject_query = re.compile(rf"{subject_name}")
    mentorrownumber = mentor_sheet.find(subject_query).row
    mentor_id = mentor_sheet.row_values(mentorrownumber)[1]
    return mentor_id


def add_row_df(df, entry):
    df.loc[-1] = entry
    df.index = df.index + 1


def empty_check(input):
    if input == '':
        return False
    return True


def next_row(sheet, col_number):
    student_list = course_sheet.col_values(col_number)

    if '' in student_list:
        return student_list.index('')+1
    else:
        return len(student_list)+1


def fetch_events(n):
    return calendarService.n_events(n)


def compare(time1, time2):
    """ 
    This function compares time and return integers based on the comparision as follows:
        if time1 == time 2 --> Return 1

        if time1 < time2   --> Return 0

        if time1 > time2   --> Return 2
    """
    return calendarService.compareTime(time1, time2)


def to_date_time(inp_time):
    return calendarService.to_date_time(inp_time)


create_enrollment_sheet("enrol_sheet")
