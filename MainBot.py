import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from Inbox import *


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=cst.token)
        self.long_poll = VkBotLongPoll(self.vk, group_id=cst.group_id)
        self.vk_api = self.vk.get_api()
        self.upload = vk_api.VkUpload(self.vk)
        self.base = {}  # {user_id: [name, last, class]}; {conf_id: [class}
        self.stat = {}  # {requests: count, users: count}

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

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())


if __name__ == "__main__":
    console_id = cst.console_id
    print(f'{cst.ver}')
    if not path.exists(get_date()):
        print('Loading schedules for current date')
        SF()
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
