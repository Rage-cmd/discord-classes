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

# create_enrollment_sheet("new_enroll")

def subject_count():
    in_sheet = sheet.worksheet("subject_sheet")
    subjects = in_sheet.col_values(3)
    length = 0
    for subject in subjects:
        print(subject.splitlines())
        length += len(subject.splitlines())

    return length-1

def insert(sheet_name,in_query, query_col,many = False,begin = 1,row = None):
    in_sheet = sheet.worksheet(sheet_name)
    if not row:
        row = next_row(in_sheet, query_col)
    
    if not many:
        course_sheet.update_cell(row, query_col, str(in_query))
    else:
        start = gspread.utils.rowcol_to_a1(row,begin)
        end = gspread.utils.rowcol_to_a1(row,begin + len(in_query)-1)
        w_range = start + ":" + end

        cell_list = in_sheet.range(w_range)
        for i in range(len(cell_list)):
            cell_list[i].value = in_query[i]
        
        in_sheet.update_cells(cell_list)


def enrolled_students(subject_number):
    return course_sheet.col_values(subject_number)


def get_sheet_list(query):
    in_sheet = sheet.worksheet(query)
    return in_sheet.get_all_values()
    

def get_row_index(sheet_name,query, column):
    #get the sheet by name
    in_sheet = sheet.worksheet(sheet_name)
    col_elements = in_sheet.col_values(column)
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


def next_row(in_sheet, col_number):
    col_list = in_sheet.col_values(col_number)
    if '' in col_list:
        return col_list.index('')+1
    else:
        return len(col_list)+1


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

def is_present(sheet_name,query, query_col):
    """
    Checks whether the worksheet with name sheet_name 
    contains the element 'query' in the column number 'query_col'
    """
    res_row = get_row_index(sheet_name,query, query_col)
    # if students was not enrolled and asked for updation inform them
    if res_row == -1:
        return False
    return True

def is_valid_date(day, month, year):
    return calendarService.is_valid_date(day,month,year)

def update_enrollment_sheet(sheet_name):
    in_sheet = sheet.worksheet(sheet_name)
    num_new_subjects = subject_count()
    num_old_subjects = len(in_sheet.row_values(1))
    print(num_old_subjects,num_new_subjects)
    if num_old_subjects != num_new_subjects:
        list_of_subjects = []
        all_subjects = [row[2] for row in get_sheet_list("subject_sheet")]
        for subjects in all_subjects:
            list_of_subjects.extend(subjects.splitlines())
        
        to_insert = list_of_subjects[num_old_subjects+1:]
        insert(sheet_name,to_insert,1,many = True,begin = num_old_subjects+1,row = 1)

update_enrollment_sheet("enrollment")

# create_enrollment_sheet("enrol_sheet")
