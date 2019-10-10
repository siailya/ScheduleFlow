from os import path, mkdir
from pickle import *

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from Inbox import *


class Bot:
    def __init__(self):
        self.classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '7А',
                        '7Б', '7В', '8А', '8Б', '8В', '9А', '9Б', '9В',
                        '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В',
                        '11Г']
        self.vk = vk_api.VkApi(
            token='46f3beec75a013ae0556c7558cf031eb56912a7ae17c2e6bd4c8c9c999006a953a9661ca31f3d28ac5dbe')
        self.long_poll = VkBotLongPoll(self.vk, group_id='187427285')
        self.vk_api = self.vk.get_api()
        self.upload = vk_api.VkUpload(self.vk)
        self.base = {}  # {user_id: [name, last, class]}; {conf_id: [class}
        self.stat = {}  # {requests: count, users: count}
        self.console_id = 2000000001
        self.whitelist = [222383631, 66061219, 223632391, 231483322]

        if not path.exists('data'):
            mkdir('data')
            pt = 'data/base.pickle'
            fi = open(pt, 'wb')
            fi.close()

            pt = 'data/stat.pickle'
            fi = open(pt, 'wb')
            fi.close()
        else:
            try:
                self.open_base()
            except:
                pass

    def main(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.obj.text:
                    Inbox(self.vk, event, self.base, self.stat)

    def write_base(self):
        pt = 'data/base.pickle'
        with open(pt, 'wb') as fi:
            dump(self.base, fi)

        pt = 'data/stat.pickle'
        with open(pt, 'wb') as fi:
            dump(self.stat, fi)

    def open_base(self):
        pt = 'data/base.pickle'
        with open(pt, 'rb') as fi:
            self.base = load(fi)

        pt = 'data/stat.pickle'
        with open(pt, 'rb') as fi:
            self.stat = load(fi)


if __name__ == "__main__":
    Bot().main()
    # print('Version 1.3.4B')
    # if not path.exists(get_date()):
    #     print('Loading schedules for current date')
    #     SF()
    #     print('Loaded!')
    # else:
    #     print()
    # print('====== Work started ======')
    # Bot().send_msg(self.console_id, f'Запущен!')
    # e = 0
    # while e <= 300:
    #     try:
    #         Bot().main()
    #     except BaseException as ex:
    #         e += 1
    #         Bot().send_msg(self.console_id, f'🆘 Exception: {ex} <count: {e} >')
