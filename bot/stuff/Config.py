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
    SCHEDULE_LINK = 'https://амтэк35.рф/wp-content/uploads/'  # date.png
    PARSE_INTERVAL = 30
    REDIRECT_DATE = '13.01.2020'

    ADMINS = [223632391, 222383631, 66061219]
    if TESTING:
        TOKEN = '46f3beec75a013ae0556c7558cf031eb56912a7ae17c2e6bd4c8c9c999006a953a9661ca31f3d28ac5dbe'
        CONSOLE = 2000000001
        GROUP_ID = 187427285
        PREFIX = '[club187427285|sftest] '
    else:
        TOKEN = 'f3d3d7283516f74feee0b753c2e0063e53ffe0bde3f9c99efd0a1ea039310eca2f6c697be8ee7c857ab06'
        CONSOLE = 2000000002
        GROUP_ID = 187161295
        PREFIX = '[club187161295|scheduleflow] '

    DIALOG_FLOW_TOKEN = 'daad299f70fe4168b16332551d267f9a'
