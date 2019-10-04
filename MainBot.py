from random import randint

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from Process import *


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(
            token='e6c8aa32f8b60fd357f2253defbee0416646b7aecea0c4caee2156c8041bf041afe691770b9975a14eb69')
        self.long_poll = VkBotLongPoll(self.vk, group_id='187161295')
        self.vk_api = self.vk.get_api()

    def photo(self, send_id, root='img.jpg'):
        request = requests.post(self.vk.method('photos.getMessagesUploadServer')[
                                    'upload_url'], files={'photo': open(root, 'rb')}).json()
        save_photo = self.vk_api.photos.saveMessagesPhoto(
            photo=request['photo'], server=request['server'], hash=request['hash'])[0]
        photo = f'photo{save_photo["owner_id"]}_{save_photo["id"]}'
        self.vk_api.messages.send(peer_id=send_id, message='',
                                  random_id=randint(-1000, 1000), attachment=photo)

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
        if (msg[-1] in 'АБВГабвг') and (msg[:-1] in '567891011'):
            if path.exists(f'{date}/{msg}.jpg'):
                self.photo(event.obj.peer_id, f'{date}/{msg.upper()}.jpg')
            else:
                self.send_msg(event.obj.peer_id, 'Сейчас все будет. Скачиваю и режу расписание')
                SF()
                self.photo(event.obj.peer_id, f'{date}/{msg.upper()}.jpg')


if __name__ == "__main__":
    Bot().main()
