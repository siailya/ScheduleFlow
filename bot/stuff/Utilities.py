from pendulum import *


TZ = 'Europe/Moscow'
FORMAT = 'DD.MM.YYYY'
EXT_FORMAT = 'DD.MM.YYYY в HH:mm'
CLASSES = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '7А',
           '7Б', '7В', '8А', '8Б', '8В', '9А', '9Б', '9В',
           '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В',
           '11Г']
NEXT_LETTER = {'А': 'Б',
               'Б': 'В',
               'В': 'Г',
               'Г': 'Д'}


def GetFormat(dialogflow_date: str):
    if '-' in dialogflow_date:
        year, month, day = list(map(int, dialogflow_date.split('-')))
        return date(year, month, day).__format__(FORMAT)
    return dialogflow_date


def ToPrint(msg):
    commands = ['расписание', 'общее расписание', 'расписание звонков', 'настройки',
                'сменить класс', 'назад', 'выключить уведомления', 'включить уведомления',
                'без выбора класса', 'на завтра', 'на сегодня', 'общее на завтра',
                'общее на сегодня', 'звонки']
    if (msg in commands) or ('расписание на' in msg) or (msg in '567891011абвг'):
        return False
    return True



