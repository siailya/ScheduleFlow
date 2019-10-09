from os import path, mkdir
from pickle import *
from random import randint

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from Process import *


class Bot:
    def __init__(self):
        self.classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '7А',
                        '7Б', '7В', '8А', '8Б', '8В', '9А', '9Б', '9В',
                        '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']
        self.vk = vk_api.VkApi(
            token='')
        self.long_poll = VkBotLongPoll(self.vk, group_id='187161295')
        self.vk_api = self.vk.get_api()
        self.upload = vk_api.VkUpload(self.vk)
        self.usr_cls = {}
        self.usrs = []

        if not path.exists('data'):
            mkdir('data')
            p = 'data/classes.pickle'
            f = open(p, 'wb')
            f.close()

            k = 'data/base.pickle'
            f = open(k, 'wb')
            f.close()
        else:
            try:
                p = 'data/classes.pickle'
                with open(p, 'rb') as f:
                    self.usr_cls = load(f)
            except:
                self.send_msg(2000000002, '1 - Все данные пользователей стерлись :)')
                self.usr_cls = {}
            try:
                k = 'data/base.pickle'
                with open(k, 'rb') as f:
                    self.usrs = load(f)
            except:
                self.send_msg(2000000002, '2 - Все данные пользователей стерлись :)')
                self.usrs = []

    def u_get(self, uid):
        info = self.vk_api.users.get(user_ids=uid)[0]
        return info['first_name'], info['last_name']

    def photo(self, send_id, root='img.jpg'):
        response = self.upload.photo_messages(root)[0]
        attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
        self.vk_api.messages.send(peer_id=send_id,
                                  message='',
                                  random_id=randint(-1000,
                                                    1000),
                                  attachment=attachment)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(
            peer_id=send_id, message=message, random_id=randint(-1000, 1000))

    def keyb(self, p_id):
        if p_id not in self.usrs:
            keyboard = VkKeyboard(one_time=False)
            keyboard.add_button('!расписание', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('!полное', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('!помощь', color=VkKeyboardColor.NEGATIVE)
            self.vk_api.messages.send(peer_id=p_id, random_id=get_random_id(),
                                      keyboard=keyboard.get_keyboard(),
                                      message='😉')
            self.usrs.append(p_id)
            with open('data/base.pickle', 'wb') as fi:
                dump(self.usrs, fi)

    def main(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.obj.text:
                self.inbox(event)
            else:
                if event.obj.peer_id <= 2000000000:
                    self.send_msg(event.obj.peer_id,
                                  '😡 Бот не умеет обрабатывать картинки, стикеры и '
                                  'пересланные сообщения! Используйте только клавиатуру '
                                  'и команду "!помощь!"')

    def inbox(self, event):
        if event.obj.text[0] != '!':
            msg = event.obj.text.replace(' ', '').replace('"', '').upper()
        else:
            msg = event.obj.text.upper()
        p_id = event.obj.peer_id
        if p_id <= 2000000000:  # Для индивидуального использования
            name, last = self.u_get(p_id)
            self.keyb(p_id)
            print(f'Сообщение от: {name} {last}\n{event.obj.text}')
            try:
                if ',' not in msg:
                    date = get_date()
                else:
                    msg, date = msg.split(',')
                    d, m = [int(i) for i in date.split('.')]
                    if abs(d - pendulum.today().day) >= 100 and msg in self.classes:
                        date = get_date()
                        self.send_msg(p_id, f'Нет расписания на этот день!\nРасписание на {date}:')
                    else:
                        date = pendulum.date(
                            pendulum.tomorrow().year, m, d).format('DD.MM.YYYY')
            except BaseException:
                date = get_date()
                self.send_msg(f'Неверный формат!\nРасписание на {date}:')

            if msg[0] != '!':
                if msg in self.classes:
                    if path.exists(f'{date}/{msg}.jpg'):
                        self.photo(p_id, f'{date}/{msg.upper()}.jpg')
                    else:
                        self.send_msg(p_id, 'Пробую найти расписание и скачать...\nЕсли вы ждете '
                                            'больше 5 секунд, то, скорее всего, все идет по плану!')
                        SF('all', date)
                        if path.exists(f'{date}/{msg.upper()}.jpg'):
                            self.send_msg(p_id, f'Расписание на {date} 😉')
                            self.photo(p_id, f'{date}/{msg.upper()}.jpg')
                        else:
                            self.send_msg(p_id, f'К сожалению, не удалось'
                                                f'найти расписание на {date} 😬')
                else:
                    pass

        if msg in ['!ПОМОЩЬ', '!КОМАНДЫ', '!СПРАВКА']:  # Общего назначения (в т.ч. и конфы)
            self.send_msg(p_id, '❓ Основные команды и справка\n\n'
                                '✅ Чтобы запросить расписание на завтра'
                                '(либо на сегодня, если время до 15:00),'
                                'просто отправьте номер класса '
                                'в удобной для вас форме: 11А, 5г, 8"В"\n\n'
                                ''
                                '📢 Если вам нужно запросить расписание в беседе, воспользуйтесь '
                                'командой "!расписание"\nТакже для беседы можно установить класс ('
                                'командой "!класс <класс>").\nВ беседах не работают команды вида '
                                '"11А", "5 г" и т.д.'
                                '\n\n'
                                ''
                                '⌚ В личныхсообщениях вы также можете после класса, через запятую, '
                                'указать желаемую дату (работает нестабильно)\n'
                                'Например - "5А, 5.10" или "11а, '
                                '7.10"\nНаличие расписания на этот день не '
                                'зависит от меня\n\n'
                                ''
                                '🚮 Если у вас произошла проблема с получением '
                                'расписания, пожалуйста, воспользуйтесь командой "!репорт", '
                                'либо напишите об этом @siailya(мне в ЛС)\n\n'
                                ''
                                '🔑===== Другие команды =====\n\n'
                                ''
                                '📚 !класс - устанавливает класс для пользователя '
                                '\n(команды "!класс 0" и "!класс сброс" '
                                'сбрасывают присвоенный класс)\n'
                                'Например: !класс 8в\n\n'
                                ''
                                '📃 !расписание - присылает расписание класса, который вы выбрали '
                                'предыдущей командой (либо полное, если класс не присвоен)\n\n'
                                ''
                                '🌐 !полное - общее расписание на сегодня/завтра в зависимости от '
                                'времени запроса\n\n'
                                ''
                                '📝 !репорт - создать отчет об ошибке, вызванной именно некоректной '
                                'работой Бота\n '
                                'Например: !репорт долго идут сообщения\n\n'
                                ''
                                '📅 !даты - список дат в этом месяце, за которые есть '
                                'сохраненные расписания')

        if '!КЛАСС' in msg:
            a = True
            try:
                cls = msg.split(' ', maxsplit=1)[1].replace(' ', '').replace('"', '')
            except BaseException:
                self.send_msg(p_id, f'Неверный формат! Используйте команду в виде "!класс '
                                    f'<номер>" (Пишите класс через пробел)')
                cls = ''
                a = False
            if cls in self.classes and a:
                self.usr_cls.update({p_id: cls})
                self.send_msg(p_id, f'Вам присвоен {cls} класс.\nТеперь вы можете использовать '
                                    f'команду "!расписание" для быстрого вызова расписания класса.')
                with open('data/classes.pickle', 'wb') as fi:
                    dump(self.usr_cls, fi)
            elif cls in ['0', 'СБРОС'] and a:
                try:
                    c = self.usr_cls.pop(p_id)
                    self.send_msg(p_id, f'Вы отписались от {c} класса!')
                    with open('data/classes.pickle', 'wb') as fi:
                        dump(self.usr_cls, fi)
                        self.send_msg(2000000002, '♻ База обновлена в файле!')
                except BaseException:
                    self.send_msg(p_id, 'Вы не подписаны на определенный класс! Используйте '
                                        'команду "!класс <номер>" (Пишите класс через пробел)')
            elif a:
                self.send_msg(p_id, f'Не бывает класса {cls}! Если это ошибка с моей стороны, '
                                    f'воспользуйтесь командой "!репорт" и кратко опишите проблему.')

        if '!РАСПИСАНИЕ' in msg:
            if p_id in self.usr_cls.keys():
                date = get_date()
                if path.exists(f'{date}/{self.usr_cls[p_id]}.jpg'):
                    self.photo(p_id, f'{date}/{self.usr_cls[p_id]}.jpg')
                else:
                    self.send_msg(p_id, 'Пробую найти расписание и скачать...\nЕсли вы ждете '
                                        'больше 5 секунд, то, скорее всего, все идет по плану!')
                    SF('all', date)
                    self.photo(p_id, f'{date}/{self.usr_cls[p_id]}.jpg')
            else:
                date = get_date()
                self.send_msg(p_id, f'Вы не выбрали класс, полное расписание:')
                get_picture(get_date(), '1')
                self.photo(p_id, f'source/{date}.png')

        elif msg == '!ДАТЫ':
            d = ''
            mnt = pendulum.now().month
            yr = pendulum.now().year
            for i in range(32):
                if i >= 10:
                    a = str(i) + '.' + str(mnt) + '.' + str(yr)
                else:
                    a = '0' + str(i) + '.' + str(mnt) + '.' + str(yr)
                if path.exists(get_date(a)):
                    d += a + '\n'
                else:
                    pass
            if d:
                d = 'Сохраненные расписания за этот месяц: \n' + d + '\n К сожалению, ' \
                                                                     'доступны только для ' \
                                                                     'запроса по классу 😒 (' \
                                                                     'Например, "11а, 5.10". Не ' \
                                                                     'работает в беседах!)'
                self.send_msg(p_id, d)
            else:
                self.send_msg(p_id, 'Произошла ошибка, либо расписаний просто нет! 😰')

        elif '!ПОЛНОЕ' in msg:
            date = get_date()
            get_picture(date, '1')
            self.photo(p_id, f'source/{date}.png')

        elif '!РЕПОРТ' in msg:
            if p_id < 2000000000:
                name, last = self.u_get(p_id)
                rep = f'⚠ Отчет об ошибке от @id{p_id}({name} {last})\n' + event.obj.text[8:]
                self.send_msg(2000000002, rep)
                self.send_msg(p_id, 'Репорт отправлен!')
            else:
                self.send_msg(p_id, 'Репорты от бесед не принимаются!')

        elif '!ПОЛЬЗОВАТЕЛИ' in msg and p_id == 2000000002:
            u = 'Список пользователей:\n'

            k = 'data/base.pickle'
            with open(k, 'wb') as fi:
                dump(self.usrs, fi)
            with open(k, 'rb') as f:
                self.usrs = load(f)
            for i in self.usrs:
                name, last = self.u_get(i)
                u += f'@id{i}({name} {last})\n'

            p = 'data/classes.pickle'
            with open(p, 'wb') as fi:
                dump(self.usr_cls, fi)
            with open(p, 'rb') as f:
                self.usr_cls = load(f)
            u += '\n\nСписок присвоенных классов:\n'
            for i in self.usr_cls.keys():
                if i < 2000000000:
                    name, last = self.u_get(i)
                    u += f'@id{i}({name} {last}) - {self.usr_cls[i]}\n'
                else:
                    u += f'Беседа {i} - {self.usr_cls[i]}\n'
            print('\n' + u)
            self.send_msg(2000000002, u)


if __name__ == "__main__":
    print('Version 1.3.4B')
    if not path.exists(get_date()):
        print('Loading schedules for current date')
        SF()
        print('Loaded!')
    else:
        print()
    print('====== Work started ======')
    Bot().send_msg(2000000002, f'Запущен!')
    e = 0
    while e <= 300:
        try:
            Bot().main()
        except BaseException as ex:
            e += 1
            Bot().send_msg(2000000002, f'🆘 Exception: {ex} <count: {e} >')
