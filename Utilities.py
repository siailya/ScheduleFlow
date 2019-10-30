from os import path, mkdir
from shutil import move
import requests
from pendulum import today, tomorrow, date, now
from vk_api import vk_api
from vk_api.utils import get_random_id

from Constantes import Constantes as cst


def get_schedule_date():
    hr = now(tz='Europe/Moscow').time().hour
    mt = now(tz='Europe/Moscow').time().minute
    yr = tomorrow().year
    mtt = tomorrow().month
    td = now().weekday()
    if td == 6:
        return tomorrow().date().__format__('DD.MM.YYYY')
    elif td in [0, 1, 2, 3, 4]:
        if (hr >= 14) and ((hr <= 23) and (mt <= 59)):
            return tomorrow().date().__format__('DD.MM.YYYY')
        else:
            return today().date().__format__('DD.MM.YYYY')
    else:
        if (hr >= 14) and ((hr <= 23) and (mt <= 59)):
            if tomorrow().day + 1 in [30, 31]:
                if mtt in [1, 3, 5, 7, 8, 10, 12]:
                    if tomorrow().day + 1 == 31:
                        return date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                    else:
                        return date(yr, mtt, 31).__format__('DD.MM.YYYY')
                else:
                    if tomorrow().day + 1 == 30:
                        return date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                    else:
                        return date(yr, mtt, 30).__format__('DD.MM.YYYY')
            else:
                return date(yr, mtt, tomorrow().day + 1).__format__('DD.MM.YYYY')
        else:
            return today().date().__format__('DD.MM.YYYY')


def send_console(s):
    vk = vk_api.VkApi(token=cst.token)
    vk_apis = vk.get_api()
    try:
        vk_apis.messages.send(peer_id=cst.console_id, message=s, random_id=get_random_id())
    except:
        vk_apis.messages.send(peer_id=cst.console_id, message='Какая-то ошибка в АПИ, но скрее '
                                                              'всего, в тебе',
                              random_id=get_random_id())


def upload_class(cls, upload):
    response = upload.photo_messages(f'{get_schedule_date()}/{cls}.png')[0]
    attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
    return attachment


def get_picture(date=get_schedule_date()):
    if not path.exists('source'):
        mkdir('source')
    if path.exists('source'):
        name = date + ".png"
        if not path.exists(f'source/{name}'):
            url = 'http://school37.com/news/data/upimages/' + date + '.png'
            p = requests.get(url)
            out = open(name, "wb")
            out.write(p.content)
            out.close()
            move(name, f'source/{name}')


def gratitude(msg):
    if len(set(msg.split()) & {'спасибо', 'спс', 'пасиб', 'сенкс', 'thank', 'от души',
                               'благодарю', 'мерси'}) >= 1:
        return True
    return False


def smile(msg):
    if len(set(list(msg)) & set(list(cst.smiles))) >= 1:
        return True
    return False
