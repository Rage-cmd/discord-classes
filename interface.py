import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import re
import math
import calendarService

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json',scope)
client = gspread.authorize(creds)

sheet = client.open('Responses')
mentor_sheet = sheet.get_worksheet(0)
student_sheet = sheet.get_worksheet(1)
course_sheet = sheet.get_worksheet(2)
schedule_sheet = sheet.get_worksheet(3)

def subject_count():
    return len(course_sheet.row_values(1))

def enrol(student_id, subject_number):
    row = next_row(course_sheet,subject_number)
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

def clear(row,column):
    del_range = course_sheet.range(row, column, row, column)
    del_range[0].value = ''
    course_sheet.update_cells(del_range,value_input_option='USER_ENTERED') 

def cell_value(row,col):
    return course_sheet.cell(row,col).value

def get_mentor_id(subject_name):
    subject_query = re.compile(rf"{subject_name}")
    mentorrownumber = mentor_sheet.find(subject_query).row
    mentor_id = mentor_sheet.row_values(mentorrownumber)[1]
    return mentor_id

def add_row_df(df,entry):
    df.loc[-1] = entry
    df.index = df.index + 1

def empty_check(input):
    if input == '':
        return False
    return True

def next_row(sheet,col_number):
    student_list = course_sheet.col_values(col_number)
    
    if '' in student_list:
        return student_list.index('')+1
    else:
        return len(student_list)+1

def fetch_events(n):
    return calendarService.n_events(n)

def compare(time1, time2):
    return calendarService.compareTime(time1,time2)