from pickle import load

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from Inbox import *


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=cst.token)
        self.long_poll = VkBotLongPoll(self.vk, group_id=cst.group_id)
        self.vk_api = self.vk.get_api()
        self.upload = vk_api.VkUpload(self.vk)
        self.base = {}  # {user_id: [name, last, class, state]}
        self.stat = {}  # {requests: count, userBs: count, thank: count}

        try:
            self.open_base()
        except:
            pass

    def main(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.inbox(event)
                write_base(self.base, self.stat)

    def inbox(self, event):
        Inbox(self.vk, event, self.base, self.stat)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())

    def open_base(self):
        pt = 'data/base.pickle'
        with open(pt, 'rb') as fi:
            self.base = load(fi)

        pt = 'data/stat.pickle'
        with open(pt, 'rb') as fi:
            self.stat = load(fi)


if __name__ == "__main__":
    # Bot().main()
    console_id = cst.console_id
    print(f'{cst.ver}')
    if not path.exists('log'):
        mkdir('log')
    if not path.exists('uploaded_photo'):
        mkdir('uploaded_photo')
    if not path.exists('data'):
        mkdir('data')
        pt = 'data/base.pickle'
        fi = open(pt, 'wb')
        fi.close()

        pt = 'data/stat.pickle'
        fi = open(pt, 'wb')
        fi.close()
    if not path.exists(f'uploaded_photo/{get_schedule_date()}.sf'):
        print('Loading schedules for current date')
        download_all()
        print('Loaded!')
    else:
        print()
    print('====== Work started ======')
    Bot().send_msg(console_id, f'Запущен! Версия {cst.ver}')
    e = 0
    while e <= 300:
        try:
            Bot().main()
        except BaseException as ex:
            e += 1
            Bot().send_msg(console_id, f'🆘 Exception: {ex} <count: {e} >')
