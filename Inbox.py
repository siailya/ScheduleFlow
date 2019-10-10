from os import path
from pickle import *

import vk_api.vk_api

from Keyboards import *
from Process import *


class Inbox:
    def __init__(self, session, event, base, stat):
        self.base = base
        self.stat = stat
        self.vk = session
        self.upload = vk_api.VkUpload(self.vk)
        self.vk_api = self.vk.get_api()

        self.admins = [222383631, 66061219, 223632391, 231483322]
        self.console_id = 2000000001

        self.user_commands = ['расписание', 'общее расписание', 'настройки']
        self.conference_commands = ['!расписание', '!общее', '!класс']

        self.nums = [str(i) for i in range(5, 12)]
        self.literas = ['а', 'б', 'в', 'г']
        self.classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '7А',
                        '7Б', '7В', '8А', '8Б', '8В', '9А', '9Б', '9В',
                        '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В',
                        '11Г']

        self.peer_id = event.obj.peer_id
        if self.peer_id == self.console_id:
            self.console(event)
        elif self.peer_id >= 2000000000 and self.peer_id != self.console_id:
            self.from_id = event.obj.from_id
            self.conference(event)
        elif self.peer_id in self.admins:
            self.user(event, True)
        else:
            self.user(event)

    def user(self, event, a=False):
        u_id = self.peer_id
        name, last = self.u_get(u_id)
        msg = event.obj.text.lower()
        if u_id not in self.admins:
            self.send_msg(self.console_id, f'Сообщение от: @id{u_id}({name} {last})\n'
                                           f'{event.obj.text}')
        # Регистрация нового пользователя
        if u_id not in self.base.keys():
            self.base.update({u_id: [name, last, 'Ns']})
            self.stat['users'] = self.stat.get('users', 0) + 1
            self.write_base()
            self.send_msg(u_id, f'Привет, {name}! Давай настроим бота под тебя. Тебе нужно просто '
                                f'указать свой класс')
            self.send_msg(self.console_id, f'Новый юзер!\nВстречайте - @id{u_id}({name} {last})')
            Keyboards(self.vk_api).class_keyboard(u_id)
        else:
            # Выбор класса:
            if msg in self.nums:
                self.base[u_id][2] = msg
                self.write_base()
                if msg in ['5', '10', '11']:
                    Keyboards(self.vk_api).litera_keyboard(u_id, True)
                else:
                    Keyboards(self.vk_api).litera_keyboard(u_id, False)
            # Выбор литеры:
            elif msg in self.literas:
                self.base[u_id][2] += msg
                self.write_base()
                self.send_msg(u_id, f'Замечательно! Вы выбрали {self.base[u_id][2].upper()} класс! '
                                    f'Этот выбор всегда можно сменить в настройках')
                if a:
                    Keyboards(self.vk_api).admin_keyboard(u_id)
                else:
                    Keyboards(self.vk_api).menu_keyboard(u_id)
            # Пользование без класса:
            elif msg == 'без выбора класса':
                self.base[u_id][2] = ''
                self.write_base()
                self.send_msg(u_id, '🙁 Без выбора класса не будет доступен весь функционал. Но '
                                    'его всегда можно выбрать в настройках 😉')
                Keyboards(self.vk_api).menu_keyboard(u_id, False)
            # Расписание
            elif msg == 'расписание':
                self.stat['requests'] = self.stat.get('requests', 0) + 1
                self.write_base()
                if path.exists(f'{get_date()}/{self.base[u_id][2].upper()}.jpg'):
                    self.photo(u_id, f'{get_date()}/{self.base[u_id][2].upper()}.jpg',
                               f'Держи расписание'
                               f'{self.base[u_id][2].upper()} '
                               f'класса на {get_date()} ☺')
                else:
                    self.send_msg(u_id, f'Сейчас попробую найти расписание на {get_date()} '
                                        f'😉\nЕсли прошло больше 10 секунд, то, скорее всего, '
                                        f'все идет по плану!')
                    SF()
                    try:
                        self.photo(u_id, f'{get_date()}/{self.base[u_id][2].upper()}.jpg',
                                   f'Держи расписание {self.base[u_id][2].upper()} '
                                   f'класса на {get_date()} ☺')
                    except:
                        self.send_msg(u_id, f'Что-то пошло не так 😲\nЯ не нашел расписание'
                                            f' {self.base[u_id][2].upper()} класса на '
                                            f'{get_date()} 😰')
            # Общее расписание
            elif msg == 'общее расписание':
                if not path.exists(f'source/{get_date()}.png'):
                    get_picture(get_date(), '1')
                self.photo(u_id, f'source/{get_date()}.png', f'Держи общее расписание'
                                                             f' на {get_date()} 😊')
            elif msg == 'настройки':
                Keyboards(self.vk_api).service_keyboard(u_id)
            elif msg == 'сменить класс':
                Keyboards(self.vk_api).class_keyboard(u_id)
            elif msg == 'назад':
                if a:
                    Keyboards(self.vk_api).admin_keyboard(u_id)
                else:
                    Keyboards(self.vk_api).menu_keyboard(u_id)
            elif msg == 'пользователи':
                if u_id in self.admins:
                    u = 'Список юзеров:\n'
                    for i in self.base.keys():
                        if i < 2000000001:
                            u += f'@id{i}({self.base[i][0]} {self.base[i][1]}) - ' \
                                 f'{self.base[i][2].upper()}\n'
                        else:
                            u += f'Беседа {i} - {self.base[i].upper()}\n'
                    self.send_msg(u_id, u)
                else:
                    self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                        'только администраторам!')
            elif msg == 'загрузить':
                if u_id in self.admins:
                    if path.exists(f'{get_date()}'):
                        self.send_msg(u_id, 'Расписание уже находится в директории!')
                    else:
                        self.send_msg(u_id, f'Попытка скачать расписание. Ход выполнения '
                                            f'отслеживается в консоли.')
                        SF()
                else:
                    self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                        'только администраторам!')
            elif msg == 'статистика':
                if u_id in self.admins:
                    self.send_msg(u_id, f'Число запросов расписания: '
                                        f'{self.stat["requests"]}\nЧисло юзеров: '
                                        f'{self.stat["users"]}')
                else:
                    self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                        'только администраторам!')
            elif msg == 'обновить':
                if u_id in self.admins:
                    SF()
                else:
                    self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                        'только администраторам!')
            elif 'общая рассылка лс' in msg:
                ms = msg[18:]
                print(ms)
                for i in self.base.keys():
                    if i < 2000000000:
                        self.send_msg(i, ms)
            elif 'общая рассылка все' in msg:
                ms = msg[19:]
                print(ms)
                for i in self.base.keys():
                    self.send_msg(i, ms)

    def console(self, event):
        msg = event.obj.text.lower()
        if msg == 'пользователи':
            u = 'Список юзеров:\n'
            for i in self.base.keys():
                if i < 2000000001:
                    u += f'@id{i}({self.base[i][0]} {self.base[i][1]}) - ' \
                         f'{self.base[i][2].upper()}\n'
                else:
                    u += f'Беседа {i} - {self.base[i][2].upper()}\n'
            self.send_msg(self.console_id, u)
        elif msg == 'загрузить':
            if path.exists(f'{get_date()}'):
                self.send_msg(self.console_id, 'Расписание уже находится в директории!')
            else:
                self.send_msg(self.console_id, f'Попытка скачать расписание. Ход выполнения '
                                               f'отслеживается в консоли.')
                SF()
                self.send_msg(self.console_id, f'Расписание на {get_date()} загружено! Ошибки '
                                               f'выше')
        elif msg == 'обновить':
            SF()
            self.send_msg(self.console_id, f'Расписание на {get_date()} обновлено!')
        elif msg == 'статистика':
            self.send_msg(self.console_id, f'Число запросов расписания: '
                                           f'{self.stat["requests"]}\nЧисло юзеров: '
                                           f'{self.stat["users"]}')
        elif 'общая рассылка лс' in msg:
            ms = msg[18:]
            print(ms)
            for i in self.base.keys():
                if i < 2000000000:
                    self.send_msg(i, ms)
        elif 'общая рассылка все' in msg:
            ms = msg[19:]
            print(ms)
            for i in self.base.keys():
                self.send_msg(i, ms)

    def conference(self, event):
        id_c = self.peer_id
        msg = event.obj.text.lower()
        if id_c not in self.base.keys():
            self.base.update({id_c: ''})
            self.write_base()
            self.send_msg(id_c, 'Привет!\nСпасибо, что добавили меня в беседу!\nВоспользуйтесь '
                                'командой "!класс <класс>", чтобы указать класс\nКоманда "!общее"'
                                'пришлет полное расписание')
        else:
            if msg in self.conference_commands or '!класс' in msg:
                if msg == '!расписание':
                    if self.base[id_c]:
                        self.stat['requests'] = self.stat.get('requests', 0) + 1
                        self.write_base()
                        if path.exists(f'{get_date()}/{self.base[id_c].upper()}.jpg'):
                            self.photo(id_c, f'{get_date()}/{self.base[id_c].upper()}.jpg',
                                       f'Держите расписание '
                                       f'{self.base[id_c].upper()} '
                                       f'класса на {get_date()} ☺')
                        else:
                            self.send_msg(id_c, f'Сейчас попробую найти расписание на {get_date()} '
                                                f'😉\nЕсли прошло больше 10 секунд, то, скорее всего, '
                                                f'все идет по плану!')
                            SF()
                            try:
                                self.photo(id_c, f'{get_date()}/{self.base[id_c].upper()}.jpg',
                                           f'Держи расписание {self.base[id_c].upper()} '
                                           f'класса на {get_date()} ☺')
                            except:
                                self.send_msg(id_c, f'Что-то пошло не так 😲\nЯ не нашел расписание'
                                                    f' {self.base[id_c].upper()} класса на '
                                                    f'{get_date()} 😰')
                    else:
                        self.send_msg(id_c, 'Вы не указали класс!\nКласс задается командой'
                                            '"!класс <класс>"\nНапример - !класс 8в')
                elif msg == '!общее':
                    if not path.exists(f'source/{get_date()}.png'):
                        get_picture(get_date(), '1')
                    self.photo(id_c, f'source/{get_date()}.png', f'Держите общее расписание'
                                                                 f' на {get_date()} 😊')
                else:
                    cls = msg.lstrip('!класс ').upper()
                    if cls in self.classes:
                        self.base.update({id_c: cls})
                        self.write_base()
                        self.send_msg(id_c, f'Вы подписались на {cls} класс! Теперь вы можете '
                                            f'воспользоваться командой "!расписание"')
                    else:
                        self.send_msg(id_c, f'Не существует класса "{cls}"! Напишите в '
                                            f'техподдержку, если это не так: @id223632391('
                                            f'Техподдержка)')

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
        with open(pt, 'wb') as fi:
            self.stat = load(fi)

    def photo(self, send_id, root='img.jpg', msg=''):
        response = self.upload.photo_messages(root)[0]
        attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
        self.vk_api.messages.send(peer_id=send_id,
                                  message=msg,
                                  random_id=get_random_id(),
                                  attachment=attachment)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())

    def u_get(self, uid):
        info = self.vk_api.users.get(user_ids=uid)[0]
        return info['first_name'], info['last_name']
