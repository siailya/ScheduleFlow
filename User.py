from os import path, listdir
from pickle import load
from random import randint

import pendulum
from vk_api import VkUpload
from vk_api.utils import get_random_id

from Base import write_base
from Constantes import Constantes as cst
from Keyboards import Keyboards
from Process import download_all
from Rings import ring_schedule
from Utilities import get_schedule_date, gratitude, smile, get_picture


class User:
    def __init__(self, vk, event, base, stat):
        self.vk = vk
        self.vk_api = self.vk.get_api()
        self.base = base
        self.stat = stat
        if event.obj.text:
            self.user(event)
        else:
            self.no_text(event)
        self.schedules = {}

    def no_text(self, event):
        u_id = event.obj.peer_id
        name, last = self.user_get(u_id)
        if 'attachments' in event.obj.keys():
            att = event.obj.attachments
            if att[0]['type'] == 'sticker':
                self.set_activity(u_id)
                self.send_console(f'Сообщение от: @id{u_id}({name} {last})\nОтправил(а) стикер')
                self.send_msg(u_id, cst.stickers[randint(0, 3)])
            elif att[0]['type'] == 'photo':
                pic_url = att[0]['photo']['sizes'][-1]['url']
                self.set_activity(u_id)
                self.send_console(f'Сообщение от: @id{u_id}({name} {last})\nОтправил(а) '
                                  f'катинку:\n{pic_url}')
                self.send_msg(u_id, cst.pics[randint(0, 2)])
            elif att[0]['type'] == 'audio':
                self.set_activity(u_id)
                self.send_console(f'Сообщение от: @id{u_id}({name} {last})\nОтправил(а) аудио')
                if randint(1, 100) > 50:
                    self.send_msg(u_id, cst.music[randint(0, 1)])
                else:
                    att = 'photo-187161295_457241548'
                    self.send_attachment(u_id, 'Ах...', att)
            else:
                self.send_console(f'Сообщение от: @id{u_id}({name} {last})\nОтправил(а) какое-то '
                                  f'необрабатываемое сообщение...')
        else:
            self.send_console(f'Сообщение от: @id{u_id}({name} {last})\nОтправил(а) какое-то '
                              f'непонятное сообщение...')

    def user(self, event):
        u_id = event.obj.peer_id
        self.set_activity(u_id)
        msg = event.obj.text.lower()
        name, last = self.user_get(u_id)
        if u_id not in cst.admins:
            if u_id in self.base.keys():
                self.send_msg(cst.console_id, f'Сообщение от: @id{u_id}({name} {last}) '
                                              f'({self.base[u_id][2]})\n'
                                              f'{event.obj.text}')
                # print(translit(f'Сообщение от: @id{u_id}({name} {last}) ({self.base[u_id][2]})'
                #                f'\n{event.obj.text}', reversed=True))
            else:
                self.send_msg(cst.console_id, f'Сообщение от: @id{u_id}({name} {last})\n'
                                              f'{event.obj.text}')
                # print(translit(f'Сообщение от: @id{u_id}({name} {last})\n{event.obj.text}',
                #                reversed=True))
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
                self.send_msg(u_id,
                              f'Замечательно! Вы выбрали {self.base[u_id][2].upper()} класс!\n'
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
                user_class = self.base[u_id][2].upper()
                if msg == 'расписание':
                    self.stat['requests'] = self.stat.get('requests', 0) + 1
                    write_base(self.base, self.stat)
                    if path.exists(f'uploaded_photo/{get_schedule_date()}.sf'):
                        self.load_schedule()
                        self.send_attachment(u_id, f'Держи расписание {user_class} класса на '
                                                   f'{get_schedule_date()} '
                                                   f'{cst.smiles_answer[randint(0, 13)]}',
                                             self.schedules[user_class])
                    else:
                        self.send_msg(u_id, f'Сейчас постараюсь найти расписание на '
                                            f'{get_schedule_date()}\nПридется чуть-чуть '
                                            f'подождать...\nЕсли '
                                            f'прошло больше 20 '
                                            f'секунд '
                                            f'- скорее всего, все идет по плану! '
                                            f'{cst.smiles_answer[randint(0, 13)]}')
                        download_all()
                        self.load_schedule()
                        try:
                            self.send_attachment(u_id, f'Держи расписание {user_class} класса на '
                                                       f'{get_schedule_date()} '
                                                       f'{cst.smiles_answer[randint(0, 13)]}',
                                                 self.schedules[user_class])
                        except:
                            self.send_msg(u_id, cst.error)
                elif msg == 'общее расписание':
                    if path.exists(f'source/{get_schedule_date()}.png'):
                        self.send_photo(u_id, f'source/{get_schedule_date()}.png',
                                        f'Держи общее расписание на {get_schedule_date()} '
                                        f'{cst.smiles_answer[randint(0, 13)]}')
                    else:
                        try:
                            get_picture()
                            self.send_photo(u_id, f'source/{get_schedule_date()}.png',
                                            f'Держи общее расписание на {get_schedule_date()} '
                                            f'{cst.smiles_answer[randint(0, 13)]}')
                        except:
                            self.send_msg(u_id, cst.error)
                elif 'расписание на' in msg:
                    try:
                        d, m = list(map(int, msg.lstrip('расписание на').split('.')))
                        date = pendulum.date(pendulum.now().year, m, d).__format__('DD.MM.YYYY')
                        if path.exists(f'source/{date}.png'):
                            self.send_photo(u_id, f'source/{date}.png', f'Держи расписание на '
                                                                        f'{date} '
                                            f'{cst.smiles_answer[randint(0, 13)]}')
                        else:
                            dates = 'Используйте команду в виде "Расписание на 20.10"\n\nСписок ' \
                                    'дат, на которые доступны расписания: \n' + \
                                    ' | '.join([s[:-9] for s in listdir('source')])
                            self.send_msg(u_id, dates)
                    except:
                        self.send_msg(u_id, cst.error)
                elif ',' in msg and '.' in msg:
                    try:
                        cls, date = msg.split(',')
                        if cls.upper() in cst.classes:
                            d, m = list(map(int, date.split('.')))
                            date = pendulum.date(pendulum.now().year, m, d).__format__('DD.MM.YYYY')
                            if not path.exists(f'uploaded_photo/{date}.sf'):
                                download_all(date)
                                with open(f'uploaded_photo/{date}.sf', 'rb') as f:
                                    self.schedules = load(f)
                                self.send_attachment(u_id, f'Держи расписание {cls.upper} класса на '
                                                           f'{date} {cst.smiles_answer[randint(0, 13)]}',
                                                     self.schedules[cls.upper()])
                            else:
                                with open(f'uploaded_photo/{date}.sf', 'rb') as f:
                                    self.schedules = load(f)
                                self.send_attachment(u_id, f'Держи расписание {cls.upper()} класса на '
                                                           f'{date} {cst.smiles_answer[randint(0, 13)]}',
                                                     self.schedules[cls.upper()])
                        else:
                            self.send_msg(u_id, f'Вряд ли у нас есть расписание {cls} класса...')
                    except FileNotFoundError:
                        cls, date = msg.split(',')
                        dates = 'Список дат, на которые доступны расписания: \n' + \
                                ' | '.join([s[:-9] for s in listdir('source')])
                        self.send_msg(u_id, f'К сожалению, у нас нет расписания на {date}\n\n'
                                            f'{dates}')
                    except KeyError:
                        cls, date = msg.split(',')
                        dates = 'Список дат, на которые доступны расписания: \n' + \
                                ' | '.join([s[:-9] for s in listdir('source')])
                        self.send_msg(u_id, f'К сожалению, у нас нет расписания {cls} класса на '
                                            f'{date}\n\n{dates}')
                    except ValueError:
                        dates = 'Список дат, на которые доступны расписания: \n' + \
                                ' | '.join([s[:-9] for s in listdir('source')])
                        self.send_msg(u_id, f'Ошибка! Скорее всего, вы некорректно указали '
                                            f'дату\n\n{dates}')
                elif msg.replace(' ', '').replace('"', '').upper() in cst.classes:
                    cls = msg.replace(' ', '').replace('"', '').upper()
                    self.stat['requests'] = self.stat.get('requests', 0) + 1
                    write_base(self.base, self.stat)
                    if path.exists(f'uploaded_photo/{get_schedule_date()}.sf'):
                        self.load_schedule()
                        self.send_attachment(u_id, f'Держи расписание {cls} класса на '
                                                   f'{get_schedule_date()} '
                                                   f'{cst.smiles_answer[randint(0, 13)]}',
                                             self.schedules[cls])
                    else:
                        self.send_msg(u_id, f'Сейчас постараюсь найти расписание на '
                                            f'{get_schedule_date()}\nПридется чуть-чуть '
                                            f'подождать...\nЕсли '
                                            f'прошло больше 20 '
                                            f'секунд '
                                            f'- скорее всего, все идет по плану! '
                                            f'{cst.smiles_answer[randint(0, 13)]}')
                        download_all()
                        self.load_schedule()
                        try:
                            self.send_attachment(u_id, f'Держи расписание {cls} класса на '
                                                       f'{get_schedule_date()} '
                                                       f'{cst.smiles_answer[randint(0, 13)]}',
                                                 self.schedules[cls])
                        except:
                            self.send_msg(u_id, cst.error)
                elif msg == 'расписание звонков':
                    ring_schedule(self.vk_api, u_id)
                elif msg == 'настройки':
                    Keyboards(self.vk_api).service_keyboard(u_id)
                elif msg == 'помощь':
                    self.send_msg(u_id, 'Мы отправили просьбу о помощи в техподдержку! Если '
                                        'разработчиков не забрали инопланетяне, они скоро '
                                        'свяжутся с вами!\nПока что прочитайте FAQ: vk.com/@scheduleflow-faq-moi-faq')
                    self.vk_api.messages.send(user_ids=cst.admins,
                                              message=f'Пользователь @id{u_id} запросил помощь!'
                                                      f'\nvk.com/gim187161295?sel={u_id}',
                                              random_id=get_random_id())
                elif msg == 'сменить класс':
                    Keyboards(self.vk_api).class_keyboard(u_id)
                    self.base[u_id][3] = 0
                elif msg == 'назад':
                    Keyboards(self.vk_api).menu_keyboard(u_id)
                elif smile(msg):
                    self.send_msg(u_id, cst.smiles_answer[randint(0, 13)])
                elif gratitude(msg):
                    self.stat['thank'] = self.stat.get('thank', 0) + 1
                    self.send_msg(u_id, cst.answers[randint(0, len(cst.answers) - 1)])
                elif 'дарова' in msg:
                    self.send_msg(u_id, 'Ну дарова, карова')
                else:
                    if randint(0, 150) >= 50:
                        self.send_msg(u_id, cst.uni[randint(0, len(cst.uni) - 1)])
                    else:
                        self.vk_api.messages.markAsRead(peer_id=u_id)

    def send_console(self, message):
        self.vk_api.messages.send(peer_id=cst.console_id,
                                  message=message,
                                  random_id=get_random_id())

    def set_activity(self, uid):
        self.vk_api.messages.setActivity(type='typing',
                                         peer_id=uid,
                                         group_id=cst.group_id)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())

    def user_get(self, uid):
        info = self.vk_api.users.get(user_ids=uid)[0]
        return info['first_name'], info['last_name']

    def send_photo(self, send_id, root='img.png', msg=''):
        self.upload = VkUpload(self.vk)
        response = self.upload.photo_messages(root)[0]
        attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
        self.vk_api.messages.send(peer_id=send_id,
                                  message=msg,
                                  random_id=get_random_id(),
                                  attachment=attachment)

    def send_attachment(self, send_id, msg, attachment):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=msg,
                                  random_id=get_random_id(),
                                  attachment=attachment)

    def load_schedule(self):
        with open(f'uploaded_photo/{get_schedule_date()}.sf', 'rb') as f:
            self.schedules = load(f)
