import os
from os import path
from sys import platform


class Config:
    VERSION = '1.8'

    TESTING = True
    DEBUGGING = False
    if platform == 'win32':
        PATH = 'C:/Projects/ScheduleFlow/'
    else:
        PATH = '/root/ScheduleFlow/'
    UPDATE_INTERVAL = 15
    SCHEDULE_LINK = 'https://амтэк35.рф/wp-content/uploads/'
    PARSE_INTERVAL = 30
    REDIRECT_DATE = '13.01.2020'

    ADMINS = [223632391, 222383631, 66061219]
    if TESTING:
        TOKEN = 'T-O-K-E-N'
        CONSOLE = 2000000001
        GROUP_ID = 187427285
        PREFIX = '[club187427285|sftest] '
    else:
        TOKEN = 'T-O-K-E-N'
        CONSOLE = 2000000002
        GROUP_ID = 187161295
        PREFIX = '[club187161295|scheduleflow] '

    DIALOG_FLOW_TOKEN = 'T-O-K-E-N'
