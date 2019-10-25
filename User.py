from os import path
from random import randint

from transliterate import translit
from vk_api import VkUpload
from vk_api.utils import get_random_id

from Base import write_base
from Constantes import Constantes as cst
from Keyboards import Keyboards
from Process import download_all
from Rings import ring_schedule
from Utilities import get_schedule_date


class User:
    def __init__(self, vk, event, base, stat):
        self.vk = vk
        self.vk_api = self.vk.get_api()
        self.base = base
        self.stat = stat
        self.upload = VkUpload(self.vk)
        self.user(event)

    def user(self, event):
        u_id = event.obj.peer_id
        msg = event.obj.text.lower()
        name, last = self.u_get(u_id)
        if u_id not in cst.admins:
            if u_id in self.base.keys():
                self.send_msg(cst.console_id, f'Сообщение от: @id{u_id}({name} {last}) '
                                              f'({self.base[u_id][2]})\n'
                                              f'{event.obj.text}')
                print(translit(f'Сообщение от: @id{u_id}({name} {last}) ({self.base[u_id][2]})'
                               f'\n{event.obj.text}', reversed=True))
            else:
                self.send_msg(cst.console_id, f'Сообщение от: @id{u_id}({name} {last})\n'
                                              f'{event.obj.text}')
                print(translit(f'Сообщение от: @id{u_id}({name} {last})\n{event.obj.text}',
                               reversed=True))
        # Регистрация нового пользователя
        if u_id not in self.base.keys():
            self.base.update({u_id: [name, last, 'Ns', 0]})
            self.stat['users'] = self.stat.get('users', 0) + 1
            write_base(self.base, self.stat)
            self.send_msg(u_id, f'Привет, {name}! Давай настроим бота под тебя. Тебе нужно просто '
                                f'указать свой класс')
            self.send_msg(cst.console_id, f'✅ Новый юзер!\nВстречайте - @id{u_id}({name} {last})')
            Keyboards(self.vk_api).class_keyboard(u_id)
        else:
            # Выбор класса:
            if (msg in ['5', '6', '7', '8', '9', '10', '11']) and (self.base[u_id][3] == 0):
                self.base[u_id][2] = msg
                self.base[u_id][3] = 1
                write_base(self.base, self.stat)
                if msg in ['5', '10', '11']:
                    Keyboards(self.vk_api).litera_keyboard(u_id, True)
                else:
                    Keyboards(self.vk_api).litera_keyboard(u_id, False)
            # Выбор литеры:
            elif (msg in 'абвг') and (self.base[u_id][3] == 1):
                self.base[u_id][2] += msg
                self.base[u_id][3] = 2
                write_base(self.base, self.stat)
                self.send_msg(u_id, f'Замечательно! Вы выбрали {self.base[u_id][2].upper()} класс!\n'
                                    f'Этот выбор всегда можно сменить в настройках')
                Keyboards(self.vk_api).menu_keyboard(u_id)
            # Пользование без класса:
            elif msg == 'без выбора класса':
                self.base[u_id][2] = ''
                self.base[u_id][3] = 2
                write_base(self.base, self.stat)
                self.send_msg(u_id, '🙁Без выбора класса не будет доступен весь функционал. Но '
                                    'его всегда можно выбрать в настройках 😉')
                Keyboards(self.vk_api).menu_keyboard(u_id, False)
            elif self.base[u_id][3] == 2:
                if msg == 'расписание':
                    self.stat['requests'] = self.stat.get('requests', 0) + 1
                    write_base(self.base, self.stat)
                    if path.exists(f'uploaded_photo/{get_schedule_date()}.sf'):
                        pass
                    else:
                        self.send_msg(u_id, f'Сейчас попробую найти расписание на {get_schedule_date()} '
                                            f'😉\nЕсли прошло больше 20 секунд, то, скорее всего, '
                                            f'все идет по плану!')
                        download_all()
                        try:
                            self.photo(u_id, f'{get_schedule_date()}/{self.base[u_id][2].upper()}.png',
                                       f'Держи расписание {self.base[u_id][2].upper()} '
                                       f'класса на {get_schedule_date()} ☺')
                        except:
                            self.send_msg(u_id, f'Что-то пошло не так 😲\nЯ не нашел расписание'
                                                f' {self.base[u_id][2].upper()} класса на '
                                                f'{get_schedule_date()} 😰')
                elif msg == 'общее расписание':
                    self.stat['requests'] = self.stat.get('requests', 0) + 1
                    write_base(self.base, self.stat)
                    if not path.exists(f'source/{get_schedule_date()}.png'):
                        get_picture(get_schedule_date(), '1')
                    self.photo(u_id, f'source/{get_schedule_date()}.png', f'Держи общее расписание '
                                                                          f'на {get_schedule_date()} 😊')
                elif msg == 'расписание звонков':
                    ring_schedule(self.vk_api, u_id)
                elif msg == 'настройки':
                    Keyboards(self.vk_api).service_keyboard(u_id)
                elif msg == 'сменить класс':
                    Keyboards(self.vk_api).class_keyboard(u_id)
                    self.base[u_id][3] = 0
                elif msg == 'назад':
                    Keyboards(self.vk_api).menu_keyboard(u_id)
                elif msg in cst.smiles:
                    self.send_msg(u_id, '😜😀😄😉😊😘😍😃😀😎✌🏻😺😸'[randint(0, 13)])
                elif 'спасибо' in msg or 'спс' in msg or 'пасиб' in msg or 'сенкс' in msg or 'thank' \
                        in msg or 'от души' in msg or 'благодарю' in msg or 'мерси' in msg:
                    self.stat['thank'] = self.stat.get('thank', 0) + 1
                    self.send_msg(u_id, cst.answers[randint(0, len(cst.answers) - 1)])
                elif 'дарова' in msg:
                    self.send_msg(u_id, 'Ну дарова, карова')

                elif 'расписание на' in msg:
                    pass

                elif ',' in msg and '.' in msg:
                    pass

    def send_console(self, message):
        self.vk_api.messages.send(peer_id=cst.console_id,
                                  message=message,
                                  random_id=get_random_id())

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())

    def u_get(self, uid):
        info = self.vk_api.users.get(user_ids=uid)[0]
        return info['first_name'], info['last_name']

    def photo(self, send_id, root='img.png', msg=''):
        response = self.upload.photo_messages(root)[0]
        attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
        self.vk_api.messages.send(peer_id=send_id,
                                  message=msg,
                                  random_id=get_random_id(),
                                  attachment=attachment)
