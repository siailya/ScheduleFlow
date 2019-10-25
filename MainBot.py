import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from Base import open_base
from Inbox import *


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=cst.token)
        self.long_poll = VkBotLongPoll(self.vk, group_id=cst.group_id)
        self.vk_api = self.vk.get_api()
        self.upload = vk_api.VkUpload(self.vk)
        self.base = {}  # {user_id: [name, last, class, state]}
        self.stat = {}  # {requests: count, userBs: count, thank: count}
        if not path.exists('tmp'):
            mkdir('tmp')
        if not path.exists('data'):
            mkdir('data')
            pt = 'data/base.pickle'
            fi = open(pt, 'wb')
            fi.close()

            pt = 'data/stat.pickle'
            fi = open(pt, 'wb')
            fi.close()
        else:
            open_base(self.base, self.stat)

    def main(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.obj.text:
                    self.inbox(event)
                    write_base(self.base, self.stat)

    def inbox(self, event):
        Inbox(self.vk, event, self.base, self.stat)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())


if __name__ == "__main__":
    console_id = cst.console_id
    print(f'{cst.ver}')
    if not path.exists(get_schedule_date()):
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
