from os import path, mkdir, remove

import requests
from pendulum import today, tomorrow, date, now
from vk_api import vk_api
from vk_api.utils import get_random_id

from Constantes import Constantes as cst


def get_schedule_date():
    hr = now(tz='Europe/Moscow').time().hour
    mt = now(tz='Europe/Moscow').time().minute
    yr = tomorrow(tz='Europe/Moscow').year
    mtt = tomorrow(tz='Europe/Moscow').month
    td = now(tz='Europe/Moscow').weekday()
    if td == 6:
        return tomorrow(tz='Europe/Moscow').date().__format__('DD.MM.YYYY')
    elif td in [0, 1, 2, 3, 4]:
        if (hr >= 13) and ((hr <= 23) and (mt <= 59)):
            return tomorrow(tz='Europe/Moscow').date().__format__('DD.MM.YYYY')
        else:
            return today(tz='Europe/Moscow').date().__format__('DD.MM.YYYY')
    else:
        if (hr >= 13) and ((hr <= 23) and (mt <= 59)):
            if tomorrow(tz='Europe/Moscow').day + 1 in [30, 31]:
                if mtt in [1, 3, 5, 7, 8, 10, 12]:
                    if tomorrow(tz='Europe/Moscow').day + 1 == 31:
                        return date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                    else:
                        return date(yr, mtt, 31).__format__('DD.MM.YYYY')
                else:
                    if tomorrow(tz='Europe/Moscow').day + 1 == 30:
                        return date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                    else:
                        return date(yr, mtt, 30).__format__('DD.MM.YYYY')
            else:
                return date(yr, mtt, tomorrow().day + 1).__format__('DD.MM.YYYY')
        else:
            return today(tz='Europe/Moscow').date().__format__('DD.MM.YYYY')


def send_console(s):
    vk = vk_api.VkApi(token=cst.token)
    vk_apis = vk.get_api()
    try:
        vk_apis.messages.send(peer_id=cst.console_id, message=s, random_id=get_random_id())
    except:
        vk_apis.messages.send(peer_id=cst.console_id, message='Какая-то ошибка в АПИ, но скрее '
                                                              'всего, в тебе',
                              random_id=get_random_id())


def upload_class(cls, upload, date):
    response = upload.photo_messages(f'{date}/{cls}.png')[0]
    attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
    return attachment


def get_picture(date=get_schedule_date()):
    if not path.exists('source'):
        mkdir('source')
    else:
        if path.exists(f'source/{date}'):
            remove(f'source/{date}')
        name = date + ".png"
        url = 'http://amtek.org/news/data/upimages/' + date + '.png'
        p = requests.get(url)
        out = open(f'source/{name}', "wb")
        out.write(p.content)
        out.close()
        if path.getsize(f'source/{name}') < 112640:
            remove(f'source/{name}')
        else:
            print('Downloaded!')


def gratitude(msg):
    for i in ['спасибо', 'спс', 'пасиб', 'сенкс', 'thank', 'от души', 'благодарю', 'мерси',
              'спасибо!', 'пасиба', 'пасибо' 'псиб', 'тсенкс', 'сэнкс']:
        if msg == i or i in msg:
            return True
    return False


def smile(msg):
    if len(set(list(msg)) & set(list(cst.smiles))) >= 1:
        return True
    return False


def hello(msg):
    p = ['привет', 'сап', 'хай']
    if msg in p or any(i in msg for i in p):
        return True
    return False


def need_out(msg):
    commands = ['расписание', 'общее расписание', 'расписание звонков', 'настройки',
                'сменить класс', 'назад', 'выключить уведомления', 'включить уведомления',
                'без выбора класса']
    if (msg in commands) or ('расписание на' in msg) or (gratitude(msg)) or (msg.upper() in cst.classes) or (msg in '567891011') or (msg in 'абвг'):
        return False
    return True
