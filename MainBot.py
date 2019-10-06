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
        classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '7А', '7Б', '7В', '8А', '8Б', '8В',
                   '9А', '9Б', '9В', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']
        msg = event.obj.text.replace(' ', '').replace('"', '').upper()
        print(msg)
        try:
            if ',' not in msg:
                date = get_date()
            else:
                msg, date = msg.split(',')
                d, m = [int(i) for i in date.split('.')]
                print(abs(d - pendulum.today().day))
                if abs(d - pendulum.today().day) >= 3 and msg in classes:
                    self.send_msg(event.obj.peer_id, 'Нет расписания на этот день! Расписание на '
                                                     'завтра:')
                    date = get_date()
                else:
                    date = pendulum.date(pendulum.tomorrow().year, m, d).format('DD.MM.YYYY')
        except:
            self.send_msg('Неверный формат! Расписание на завтра (либо понедельник, если сегодня '
                          'суббота):')
            date = get_date()

        if msg[0] != '!':
            print(date)
            if msg in classes:
                if path.exists(f'{date}/{msg}.jpg'):
                    self.photo(event.obj.peer_id, f'{date}/{msg.upper()}.jpg')
                else:
                    self.send_msg(event.obj.peer_id, 'Пробую найти расписание и скачать...\nЕсли '
                                                     'вы ждете больше 5 секунд, то, скорее всего,'
                                                     'все идет по плану!')
                    SF('all', date)
                    if path.exists(f'{date}/{msg.upper()}.jpg'):
                        self.send_msg(event.obj.peer_id, f'Расписание на {date} 😉')
                        self.photo(event.obj.peer_id, f'{date}/{msg.upper()}.jpg')
                    else:
                        self.send_msg(event.obj.peer_id, f'К сожалению, не удалось найти '
                                                         f'расписание на {date} 😬')
            else:
                self.send_msg(event.obj.peer_id, 'Такого класса не существует!\nПри вводе класса '
                                                 'используйте только цифры и кириллицу!\nНапример '
                                                 '-  11А, 9"В", 10 г, 5 "а"')
        else:
            if msg in ['!ПОМОЩЬ', '!КОМАНДЫ', '!СПРАВКА']:
                self.send_msg(event.obj.peer_id, '❗ Чтобы запросить расписание на завтра, '
                                                 'просто отправьте '
                                                 'номер класса в удобной для вас форме:\n'
                                                 '11А, 5г, 8"В"\n\n'
                                                 ''
                                                 '⌚ Вы также можете попытать удачу (так как эта '
                                                 'функция работает крайне нестабильно) и '
                                                 'после класса, через запятую, '
                                                 'указать желаемую дату\n'
                                                 'Например - "5А, 5.10" или "11а, '
                                                 '7.10"\nНаличие расписания на этот день не '
                                                 'зависит от меня, т.к. я не храню его копии '
                                                 'локально\n\n'
                                                 ''
                                                 '🚮 Если у вас произошла проблема с получением '
                                                 'расписания, пожалуйста, напишите об этом '
                                                 '@siailya(мне в ЛС)\n\n'
                                                 ''
                                                 '🔑===== Другие команды ====-\n'
                                                 'Опции находятся в разработке')


if __name__ == "__main__":
    e = 0
    while e <= 200:
        try:
            Bot().main()
        except:
            e += 1
            print('Ошибка', e)
