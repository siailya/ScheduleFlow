from random import randint

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from Process import *


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(
            token='')
        self.long_poll = VkBotLongPoll(self.vk, group_id='187161295')
        self.vk_api = self.vk.get_api()
        self.upload = vk_api.VkUpload(self.vk)

    def photo(self, send_id, root='img.jpg'):
        response = self.upload.photo_messages(root)[0]
        attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
        self.vk_api.messages.send(peer_id=send_id, message='',
                                  random_id=randint(-1000, 1000), attachment=attachment)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(
            peer_id=send_id, message=message, random_id=randint(-1000, 1000))

    def main(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.inbox(event)

    def inbox(self, event):
        msg = event.obj.text.replace(' ', '').replace('"', '').upper()
        date = get_tomorrow_date()
        if msg in ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '7А', '7Б', '7В', '8А', '8Б', '8В',
                   '9А', '9Б', '9В', '10А', '810Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']:
            if path.exists(f'{date}/{msg}.jpg'):
                self.photo(event.obj.peer_id, f'{date}/{msg.upper()}.jpg')
            else:
                self.send_msg(event.obj.peer_id, 'Сейчас все будет. Скачиваю и режу расписание')
                SF()
                self.photo(event.obj.peer_id, f'{date}/{msg.upper()}.jpg')
        else:
            self.send_msg(event.obj.peer_id, 'Такого класса не существует!\nПри вводе класса '
                                             'используйте только цифры и кириллицу!\nНапример - '
                                             '11А, 9"В", 10 Г ')


if __name__ == "__main__":
    e = 0
    while True and e <= 100:
        try:
            Bot().main()
        except:
            e += 1
            print('Ошибка!', e)
