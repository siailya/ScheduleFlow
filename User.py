import json
from os import path, listdir, remove
from pickle import load
from random import randint

import apiai as apiai
import pendulum
from pendulum import *
from vk_api import VkUpload
from vk_api.utils import get_random_id

from Base import *
from Constantes import Constantes as cst
from Keyboards import Keyboards
from Process import download_all
from Rings import ring_schedule
from Utilities import gratitude, smile


def saturday():
    if pendulum.tomorrow(tz='Europe/Moscow').day == 31:
        return pendulum.date(pendulum.tomorrow().year, pendulum.tomorrow().month + 1, 1).__format__('DD.MM.YYYY')
    elif pendulum.tomorrow(tz='Europe/Moscow').day == 30:
        if pendulum.tomorrow().month in [2, 4, 6, 9, 11]:
            return pendulum.date(pendulum.tomorrow().year, pendulum.tomorrow().month + 1, 1).__format__('DD.MM.YYYY')
        else:
            return pendulum.date(pendulum.tomorrow().year, pendulum.tomorrow().month, 31).__format__('DD.MM.YYYY')
    else:
        return pendulum.date(pendulum.tomorrow().year, pendulum.tomorrow().month,
                             pendulum.tomorrow().day + 1).__format__('DD.MM.YYYY')


def get_schedule_date():
    hr = now(tz='Europe/Moscow').time().hour
    mt = now(tz='Europe/Moscow').time().minute
    yr = tomorrow(tz='Europe/Moscow').year
    mtt = tomorrow(tz='Europe/Moscow').month
    td = now(tz='Europe/Moscow').weekday()
    if td == 6:
        return tomorrow(tz='Europe/Moscow').date().__format__('DD.MM.YYYY')
    elif td in [0, 1, 2, 3, 4]:
        if (hr >= 13) and ((hr <= 23) and (mt <= 59)):
            return tomorrow(tz='Europe/Moscow').date().__format__('DD.MM.YYYY')
        else:
            return today(tz='Europe/Moscow').date().__format__('DD.MM.YYYY')
    else:
        if (hr >= 13) and ((hr <= 23) and (mt <= 59)):
            if tomorrow(tz='Europe/Moscow').day + 1 in [30, 31]:
                if mtt in [1, 3, 5, 7, 8, 10, 12]:
                    if tomorrow(tz='Europe/Moscow').day + 1 == 31:
                        return date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                    else:
                        return date(yr, mtt, 31).__format__('DD.MM.YYYY')
                else:
                    if tomorrow(tz='Europe/Moscow').day + 1 == 30:
                        return date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                    else:
                        return date(yr, mtt, 30).__format__('DD.MM.YYYY')
            else:
                return date(yr, mtt, tomorrow().day + 1).__format__('DD.MM.YYYY')
        else:
            return today(tz='Europe/Moscow').date().__format__('DD.MM.YYYY')


class User:
    def __init__(self, vk, event, base):
        self.vk = vk
        self.vk_api = self.vk.get_api()
        self.db = base
        if event.obj.text:
            self.user(event)
        else:
            self.no_text(event)
        self.schedules = {}
        self.load_schedule(get_schedule_date())

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
        if u_id not in [i[0] for i in get_all_ids(self.db)]:
            name, last = self.user_get(u_id)
            self.send_msg(u_id, f'Привет, {name}! Давай настроим бота под тебя.\nТебе нужно просто '
                                f'указать свой класс')
            self.send_console(f'✅ Новый юзер!\nВстречайте: @id{u_id}({name} {last})')
            Keyboards(self.vk_api).class_keyboard(u_id)
            new_user(self.db, u_id, name, last)
        else:
            if (msg in '5 6 7 8 9 10 11') and (get_state(self.db, u_id) == 0):
                set_class_num(self.db, u_id, int(msg))
                set_state(self.db, u_id, 1)
                if msg in ['5', '10', '11']:
                    Keyboards(self.vk_api).litera_keyboard(u_id, True)
                else:
                    Keyboards(self.vk_api).litera_keyboard(u_id, False)
            elif (msg in 'абвг') and (get_state(self.db, u_id) == 1):
                name, last = self.user_get(u_id)
                set_class_lit(self.db, u_id, msg.upper())
                set_state(self.db, u_id, 2)
                self.send_msg(u_id, f'Замечательно! Вы выбрали {get_cls(self.db, u_id).upper()} класс!\n'
                                    f'Этот выбор всегда можно сменить в настройках')
                self.send_console(
                    f'Пользователь @id{u_id}({name} {last}) выбрал {get_cls(self.db, u_id).upper()} класс')
                Keyboards(self.vk_api).menu_keyboard(u_id)
            elif msg == 'без выбора класса':
                set_state(self.db, u_id, 2)
                self.send_msg(u_id, '🙁Без выбора класса не будет доступен весь функционал. Но '
                                    'его всегда можно выбрать в настройках 😉')
                Keyboards(self.vk_api).menu_keyboard(u_id, False)
            elif get_state(self.db, u_id) == 2:
                name, last, cls, requests = get_by_id(self.db, u_id)[0]
                # if need_out(msg) and u_id not in cst.admins:
                #     self.send_console(f'Сообщение от: @id{u_id}({name} {last}) ({cls}):\n'
                #                       f'{event.obj.text}')
                if 'расписание на' in msg:
                    increase_requests(self.db, u_id)
                    try:
                        d, m = list(map(int, msg.lstrip('расписание на').split('.')))
                        all_date = pendulum.date(pendulum.now().year, m, d).__format__('DD.MM.YYYY')
                        print(all_date)
                        self.load_schedule(all_date)
                        if path.exists(f'uploaded_photo/{all_date}.sf'):
                            self.send_attachment(u_id, f'Держи общее расписание на {all_date} {cst.smiles_answer[randint(0, 13)]}',
                                                 self.schedules['main'])
                        else:
                            dates = 'Используйте команду в виде "Расписание на 20.10"\n\nСписок ' \
                                    'дат, на которые доступны расписания: \n' + \
                                    ' | '.join([s[:-9] for s in listdir('source')])
                            self.send_msg(u_id, dates)
                    except:
                        self.send_msg(u_id, cst.error)
                elif ',' in msg and '.' in msg and any([i.lower() in msg for i in cst.classes]):
                    increase_requests(self.db, u_id)
                    try:
                        cls, schedule_date = msg.split(',')
                        if cls.upper() in cst.classes:
                            d, m = list(map(int, schedule_date.split('.')))
                            schedule_date = pendulum.date(pendulum.now().year, m, d).__format__('DD.MM.YYYY')
                            if not path.exists(f'uploaded_photo/{schedule_date}.sf'):
                                self.send_msg(u_id,
                                              'Сейчас попробую найти или скачать расписание с сайта!\nЧуть-чуть терпения!')
                                download_all(schedule_date)
                                try:
                                    with open(f'uploaded_photo/{schedule_date}.sf', 'rb') as f:
                                        self.schedules = load(f)
                                    self.send_attachment(u_id, f'Держи расписание {cls.upper()} класса на '
                                                               f'{schedule_date} {cst.smiles_answer[randint(0, 13)]}',
                                                         self.schedules[cls.upper()])
                                except:
                                    dates = 'Список дат, на которые доступны расписания: \n' + \
                                            ' | '.join([s[:-9] for s in listdir('source')])
                                    self.send_msg(u_id, f'Ошибка! Расписание на указанную дату не найдено!\n\n{dates}')
                            else:
                                try:
                                    with open(f'uploaded_photo/{schedule_date}.sf', 'rb') as f:
                                        self.schedules = load(f)
                                    self.send_attachment(u_id, f'Держи расписание {cls.upper()} класса на '
                                                               f'{schedule_date} {cst.smiles_answer[randint(0, 13)]}',
                                                         self.schedules[cls.upper()])
                                except:
                                    remove(f'uploaded_photo/{schedule_date}.sf')
                                    dates = 'Список дат, на которые доступны расписания: \n' + \
                                            ' | '.join([s[:-9] for s in listdir('source')])
                                    self.send_msg(u_id, f'Ошибка! Расписание на указанную дату не найдено!\n\n{dates}')
                        else:
                            self.send_msg(u_id, f'Вряд ли у нас есть расписание {cls} класса...')
                    except FileNotFoundError:
                        cls, err_date = msg.split(',')
                        dates = 'Список дат, на которые доступны расписания: \n' + \
                                ' | '.join([s[:-9] for s in listdir('source')])
                        self.send_msg(u_id, f'К сожалению, у нас нет расписания на {err_date}\n\n'
                                            f'{dates}')
                    except KeyError:
                        cls, err_date = msg.split(',')
                        dates = 'Список дат, на которые доступны расписания: \n' + \
                                ' | '.join([s[:-9] for s in listdir('source')])
                        self.send_msg(u_id, f'К сожалению, у нас нет расписания {cls} класса на '
                                            f'{err_date}\n\n{dates}')
                    except ValueError:
                        dates = 'Список дат, на которые доступны расписания: \n' + \
                                ' | '.join([s[:-9] for s in listdir('source')])
                        self.send_msg(u_id, f'Ошибка! Скорее всего, вы некорректно указали '
                                            f'дату\n\n{dates}')
                elif msg == 'на завтра':
                    increase_requests(self.db, u_id)
                    if pendulum.today(tz='Europe/Moscow').weekday() == 5:
                        schedule_date = saturday()
                    else:
                        schedule_date = pendulum.tomorrow(tz='Europe/Moscow').__format__('DD.MM.YYYY')

                    if not path.exists(f'uploaded_photo/{schedule_date}.sf'):
                        if path.exists(f'source/{schedule_date}.png'):
                            remove(f'source/{schedule_date}.png')
                        self.send_msg(u_id,
                                      'Сейчас попробую найти или скачать расписание с сайта!\nЧуть-чуть терпения!')
                        download_all(schedule_date)
                        try:
                            self.load_schedule(schedule_date)
                            if pendulum.today(tz='Europe/Moscow').weekday() != 5:
                                self.send_attachment(u_id,
                                                     f'Держи расписание на завтра! {cst.smiles_answer[randint(0, 13)]}',
                                                     self.schedules[get_cls(self.db, u_id)])
                            else:
                                self.send_attachment(u_id,
                                                     f'Держи расписание на понедельник! {cst.smiles_answer[randint(0, 13)]}',
                                                     self.schedules[get_cls(self.db, u_id)])
                        except:
                            self.send_msg(
                                cst.error + 'Произошла ошибка!\nПо-прежнему доступна команда "Расписание", попробуйте её')
                    else:
                        try:
                            self.load_schedule(schedule_date)
                            if pendulum.today(tz='Europe/Moscow').weekday() != 5:
                                self.send_attachment(u_id,
                                                     f'Держи расписание на завтра! {cst.smiles_answer[randint(0, 13)]}',
                                                     self.schedules[get_cls(self.db, u_id)])
                            else:
                                self.send_attachment(u_id,
                                                     f'Держи расписание на понедельник! {cst.smiles_answer[randint(0, 13)]}',
                                                     self.schedules[get_cls(self.db, u_id)])
                        except:
                            self.send_msg(u_id,
                                          cst.error + '\nПо-прежнему доступна команда "Расписание", попробуйте её')
                elif msg == 'на сегодня':
                    increase_requests(self.db, u_id)
                    if pendulum.today(tz='Europe/Moscow').weekday() == 6:
                        self.send_msg(u_id, 'Сегодня воскресенье!\nПопробуй запросить расписание на завтра ;-)')
                    else:
                        schedule_date = pendulum.today(tz='Europe/Moscow').__format__('DD.MM.YYYY')
                        if not path.exists(f'uploaded_photo/{schedule_date}.sf'):
                            if path.exists(f'source/{schedule_date}.png'):
                                remove(f'source/{schedule_date}.png')
                            self.send_msg(u_id,
                                          'Сейчас попробую найти или скачать расписание с сайта!\nЧуть-чуть терпения!')
                            download_all(schedule_date)
                            try:
                                self.load_schedule(schedule_date)
                                self.send_attachment(u_id,
                                                     f'Держи расписание на сегодня!  {cst.smiles_answer[randint(0, 13)]}',
                                                     self.schedules[get_cls(self.db, u_id)])
                            except:
                                self.send_msg(u_id,
                                              cst.error + '\nПо-прежнему доступна команда "Расписание", попробуйте её 😉')
                        else:
                            try:
                                self.load_schedule(schedule_date)
                                self.send_attachment(u_id,
                                                     f'Держи расписание на сегодня! {cst.smiles_answer[randint(0, 13)]}',
                                                     self.schedules[get_cls(self.db, u_id)])
                            except:
                                self.send_msg(u_id,
                                              cst.error + '\nПо-прежнему доступна команда "Расписание", попробуйте её 😉')
                elif msg == 'общее на сегодня':
                    increase_requests(self.db, u_id)
                    if pendulum.today(tz='Europe/Moscow').weekday() == 6:
                        self.send_msg(u_id, 'Сегодня воскресенье!\nПопробуй запросить расписание на завтра ;-)')
                    else:
                        schedule_date = pendulum.today(tz='Europe/Moscow').__format__('DD.MM.YYYY')

                        self.main_schedule_by_date(u_id, schedule_date)
                elif msg == 'общее на завтра':
                    increase_requests(self.db, u_id)
                    if pendulum.today(tz='Europe/Moscow').weekday() == 5:
                        schedule_date = saturday()
                    else:
                        schedule_date = pendulum.tomorrow(tz='Europe/Moscow').__format__('DD.MM.YYYY')

                    self.main_schedule_by_date(u_id, schedule_date)
                elif msg == 'звонки':
                    ring_schedule(self.vk_api, u_id)
                elif msg == 'настройки':
                    set_state(self.db, u_id, 3)
                    Keyboards(self.vk_api).service_keyboard(u_id, get_notifications(self.db, u_id))
                elif gratitude(msg):
                    increase_gratitude(self.db, u_id)
                    self.send_msg(u_id, self.dialog_flow(msg))
                elif smile(msg):
                    self.send_msg(u_id, cst.smiles_answer[randint(0, 13)])
                else:
                    answer = self.dialog_flow(msg)
                    self.send_console(f'Сообщение от: @id{u_id}({name} {last})\n- {msg}\n- {answer}')
                    self.send_msg(u_id, answer)
            elif get_state(self.db, u_id) == 3:
                name, last, cls, requests = get_by_id(self.db, u_id)[0]
                if msg == 'помощь':
                    self.send_msg(u_id, 'Мы отправили просьбу о помощи в техподдержку! Если '
                                        'разработчиков не забрали инопланетяне, они скоро '
                                        'свяжутся с вами!\nПока что прочитайте FAQ: vk.com/@scheduleflow-faq-moi-faq')
                    self.vk_api.messages.send(user_ids=cst.admins,
                                              message=f'Пользователь @id{u_id} запросил помощь!'
                                                      f'\nvk.com/gim187161295?sel={u_id}',
                                              random_id=get_random_id())
                elif msg == 'сменить класс':
                    set_state(self.db, u_id, 0)
                    Keyboards(self.vk_api).class_keyboard(u_id)
                elif msg == 'назад':
                    set_state(self.db, u_id, 2)
                    if get_cls(self.db, u_id) != 'Ns':
                        Keyboards(self.vk_api).menu_keyboard(u_id)
                    else:
                        Keyboards(self.vk_api).menu_keyboard(u_id, False)
                elif msg == 'выключить уведомления':
                    set_notifications(self.db, u_id, 0)
                    Keyboards(self.vk_api).service_keyboard(u_id, 0, 'Уведомления выключены!')
                    self.send_console(f'Пользователь @id{u_id}({name} {last}) выключил уведомления')
                elif msg == 'включить уведомления':
                    set_notifications(self.db, u_id, 1)
                    Keyboards(self.vk_api).service_keyboard(u_id, 1, 'Уведомления включены!')
                    self.send_console(f'Пользователь @id{u_id}({name} {last}) включил уведомления')
                else:
                    self.send_msg(u_id, 'Чтобы продолжить работу, выйдите из панели управления 😉')

    def send_console(self, message):
        self.vk_api.messages.send(peer_id=cst.console_id,
                                  message=message,
                                  random_id=get_random_id())

    def set_activity(self, uid):
        self.vk_api.messages.setActivity(type='typing',
                                         peer_id=uid,
                                         group_id=cst.group_id)

    def main_schedule_by_date(self, u_id, schedule_date):
        if path.exists(f'uploaded_photo/{schedule_date}.sf'):
            self.load_schedule(schedule_date)
            self.send_attachment(u_id,
                                 f'Держи общее расписание на {schedule_date} {cst.smiles_answer[randint(0, 13)]}',
                                 self.schedules['main'])
        else:
            try:
                download_all(schedule_date)
                self.load_schedule(schedule_date)
                self.send_attachment(u_id,
                                     f'Держи общее расписание на {schedule_date} {cst.smiles_answer[randint(0, 13)]}',
                                     self.schedules['main'])
            except:
                self.send_msg(u_id, cst.error)

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

    def load_schedule(self, date=get_schedule_date()):
        with open(f'uploaded_photo/{date}.sf', 'rb') as f:
            self.schedules = load(f)

    def dialog_flow(self, message_text):
        request = apiai.ApiAI(cst.ai_token).text_request()
        request.lang = 'ru'
        request.session_id = 'SFTest'
        request.query = message_text
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech']
        if response:
            return response
        else:
            return 'Я тебя не понимаю, прости'
