import sqlite3

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from Base import add_new_day, del_by_id
from Inbox import *


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=cst.token)
        self.long_poll = VkBotLongPoll(self.vk, group_id=cst.group_id)
        self.vk_api = self.vk.get_api()
        self.upload = vk_api.VkUpload(self.vk)
        self.base = {}  # {user_id: [name, last, class, state]}
        self.stat = {}  # {requests: count, userBs: count, thank: count}
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
    Bot().main()
    # console_id = cst.console_id
    # print(f'{cst.ver}')
    # if not path.exists('log'):
    #     mkdir('log')
    # if not path.exists('uploaded_photo'):
    #     mkdir('uploaded_photo')
    # if not path.exists('data'):
    #     mkdir('data')
    #     pt = 'data/base.pickle'
    #     fi = open(pt, 'wb')
    #     fi.close()
    #
    #     pt = 'data/stat.pickle'
    #     fi = open(pt, 'wb')
    #     fi.close()
    # if not path.exists(f'uploaded_photo/{get_schedule_date()}.sf'):
    #     print('Loading schedules for current date')
    #     download_all()
    #     print('Loaded!')
    # else:
    #     print()
    # print('====== Work started ======')
    # try:
    #     Bot().send_msg(console_id, f'Запущен! Версия {cst.ver}')
    # except:
    #     sleep(60)
    # e = 0
    # while e <= 300:
    #     try:
    #         Bot().main()
    #     except BaseException as ex:
    #         e += 1
    #         try:
    #             Bot().send_msg(console_id, f'🆘 Exception: {ex} <count: {e} >')
    #         except:
    #             sleep(60)