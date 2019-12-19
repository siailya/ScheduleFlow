import sqlite3
from time import sleep

import vk_api.vk_api
from pendulum import today, tomorrow, date
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from Base import add_new_day, del_by_id
from Inbox import *


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


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=cst.token)
        self.long_poll = VkBotLongPoll(self.vk, group_id=cst.group_id)
        self.vk_api = self.vk.get_api()
        self.db = sqlite3.connect('data/base.db')

    def main(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                add_new_day(self.db)
                self.inbox(event)
            elif event.type == VkBotEventType.MESSAGE_DENY:
                name, last = self.user_get(event.obj.user_id)
                del_by_id(self.db, event.obj.user_id)
                self.send_console(f'🚫 Пользователь @id{event.obj.user_id}({name} {last}) запретил сообщения и был удален из базы')
            elif event.type == VkBotEventType.GROUP_JOIN:
                name, last = self.user_get(event.obj.user_id)
                self.send_console(f'🔓 Новый подписчик: @id{event.obj.user_id}({name} {last})')
            elif event.type == VkBotEventType.GROUP_LEAVE:
                name, last = self.user_get(event.obj.user_id)
                self.send_console(f'🔒 Произошло то, чего я не ожидал...\n'
                                  f'В общем, подписчик пропал...\n'
                                  f'@id{event.obj.user_id}({name} {last})')
            elif event.type == VkBotEventType.WALL_REPLY_NEW:
                name, last = self.user_get(event.obj.from_id)
                self.send_console(f'Пользователь @id{event.obj.from_id}({name} {last}) оставил комментарий:\n{event.obj.text}')

    def inbox(self, event):
        Inbox(self.vk, event, self.db)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())

    def send_console(self, msg):
        self.vk_api.messages.send(peer_id=cst.console_id,
                                  message=msg,
                                  random_id=get_random_id())

    def user_get(self, uid):
        info = self.vk_api.users.get(user_ids=uid)[0]
        return info['first_name'], info['last_name']


if __name__ == "__main__":
    if cst.debug:
        Bot().main()
    else:
        console_id = cst.console_id
        print(f'{cst.ver}')
        if not path.exists('log'):
            mkdir('log')
        if not path.exists('uploaded_photo'):
            mkdir('uploaded_photo')
        if not path.exists('data'):
            mkdir('data')
        if not path.exists('statistic'):
            mkdir('statistic')
        if not path.exists('tmp'):
            mkdir('tmp')
        if not path.exists(f'uploaded_photo/{get_schedule_date()}.sf'):
            print('Loading schedules for current date')
            download_all(get_schedule_date())
            print('Loaded!')
        else:
            print()
        print('====== Work started ======')
        try:
            Bot().send_msg(console_id, f'Запущен! Версия {cst.ver}')
        except:
            sleep(60)
        e = 0
        while e <= 300:
            try:
                Bot().main()
            except BaseException as ex:
                e += 1
                try:
                    Bot().send_msg(console_id, f'🆘 Exception: {ex} <count: {e} >')
                except:
                    sleep(60)