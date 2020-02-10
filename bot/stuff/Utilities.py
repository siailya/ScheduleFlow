from pendulum import *


INIT_TIME = 0
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
GD = {'5А': 'https://drive.google.com/open?id=0B7EhlYtylzDbRmRVdk1HX2lOT1U',
      '5Б': 'https://drive.google.com/open?id=0B7EhlYtylzDbTnZoNnd1Wk9SckU',
      '5В': 'https://drive.google.com/open?id=0B7EhlYtylzDbRXFHVUtHVG5JZkk',
      '5Г': 'https://drive.google.com/open?id=1X0wGQXPfVU8ub1ROZjEs892x4Hd-RKH2',
      '6А': 'https://drive.google.com/open?id=0B50-jDbZypbpbFZ6SHRlSFhYMXc',
      '6Б': 'https://drive.google.com/open?id=0B50-jDbZypbpaDllajVyTXdzV2c',
      '6В': 'https://drive.google.com/open?id=0B50-jDbZypbpVVBZVkkwM29WREk',
      '7А': 'https://drive.google.com/open?id=0B50-jDbZypbpcDQ3MEVjdTBQMnc',
      '7Б': 'https://drive.google.com/open?id=0B50-jDbZypbpMER1d2VHS29LQzg',
      '7В': 'https://drive.google.com/open?id=0B50-jDbZypbpZVRqZ1hiTEpodTg',
      '8А': 'https://drive.google.com/open?id=0B50-jDbZypbpMFNCaHhMT3EzX1k',
      '8Б': 'https://drive.google.com/open?id=0B50-jDbZypbpbHlrWk9OZlBmRVk',
      '8В': 'https://drive.google.com/open?id=0B50-jDbZypbpXy1NaHVCbG02TEU',
      '9А': 'https://drive.google.com/open?id=0B50-jDbZypbpSHducGZlVFNRcU0',
      '9Б': 'https://drive.google.com/open?id=0B50-jDbZypbpelN3aUE4TnJ0bDg',
      '9В': 'https://drive.google.com/open?id=0B50-jDbZypbpNVV1LWF2Q0kzbjQ',
      '10А': 'https://drive.google.com/open?id=0B50-jDbZypbpNjdxYnBGQmhZQms',
      '10Б': 'https://drive.google.com/open?id=0B50-jDbZypbpUmR5R1BFb2kySnc',
      '10В': 'https://drive.google.com/open?id=0B50-jDbZypbpM2J1Rm9lY3U3QWc',
      '10Г': 'https://drive.google.com/open?id=0B7EhlYtylzDbaGh0UHdQYUUyT2c',
      '11А': 'https://drive.google.com/open?id=0B50-jDbZypbpUzlFMEpOSkNBanc',
      '11Б': 'https://drive.google.com/open?id=0B50-jDbZypbpenRDWmZ0eDI3d1k',
      '11В': 'https://drive.google.com/open?id=0B50-jDbZypbpbTRJQkJzbHlMRUE',
      '11Г': 'https://drive.google.com/open?id=1CTP04pWS4PPcC-zY7P4nIPpQFphpCsyc',
      'main': 'https://drive.google.com/open?id=0B50-jDbZypbpYVhBcW04NnhwZk0'}


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



