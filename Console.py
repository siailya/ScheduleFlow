from math import ceil
from os import remove
from pickle import load, dump
from random import randint
from shutil import rmtree, copy

import matplotlib.pyplot as plt
import pendulum
import vk_api
from pendulum import today, date, tomorrow
from vk_api import VkUpload
from vk_api.utils import get_random_id

from Base import *
from Constantes import Constantes as cst
from Process import download_all
from Utilities import get_picture, upload_class, upload_pic


def saturday():
    if tomorrow(tz='Europe/Moscow').day == 31:
        return date(tomorrow().year, tomorrow().month + 1, 1).__format__('DD.MM.YYYY')
    elif tomorrow(tz='Europe/Moscow').day == 30:
        if tomorrow().month in [2, 4, 6, 9, 11]:
            return date(tomorrow().year, tomorrow().month + 1, 1).__format__('DD.MM.YYYY')
        else:
            return date(tomorrow().year, tomorrow().month, 31).__format__('DD.MM.YYYY')
    else:
        return date(tomorrow().year, tomorrow().month, tomorrow().day + 1).__format__('DD.MM.YYYY')


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


class Console:
    def __init__(self, vk_api_get, event, base, vk):
        self.vk_api = vk_api_get
        self.vk = vk
        self.db = base
        self.schedules = {}
        if event.obj.text:
            self.console(event)
        else:
            if randint(0, 100) >= 90:
                self.send_console('Очень интересно')

    def console(self, event):
        # Keyboards(self.vk_api).conslole_keyboard()
        msg = event.obj.text.lower().replace('@', '')
        if msg == '[club187161295|scheduleflow] обновить':
            update_time = get_schedule_date()
            self.send_console(f'Сейчас {now(tz="Europe/Moscow").__format__("DD.MM.YYYY HH:mm")}\nЗагрузка расписания на {update_time}')
            a = ''
            try:
                rmtree(f'{update_time}')
                a += 'Каталог со старым расписанием удален!\n'
            except FileNotFoundError:
                a += 'Каталог не найден!\n'

            try:
                remove(f'source/{update_time}.png')
                a += 'Старый исходник удален!'
            except FileNotFoundError:
                a += 'Старый исходник не найден'

            self.send_console(a)
            get_picture(update_time)
            download_all(update_time)
            self.load_schedule()
            self.send_console(f'Расписание на {update_time} обновлено!')
        elif msg == '[club187161295|scheduleflow] статистика':
            self.get_stat()
        elif msg == '[club187161295|scheduleflow] полная статистика':
            self.full_stat()
        elif 'общая рассылка лс' in msg:
            text = event.obj.text[18:]
            send_ids = [i[0] for i in get_all_ids(self.db)]
            for i in range(ceil(len(send_ids) / 99)):
                self.send_many_users(send_ids[99 * i: 99 * (i + 1)], text)
        elif 'рассылка класс' in msg:
            try:
                cls, text = event.obj.text.split('_')
                print(cls, text)
                cls = cls[15:].upper()
                send_ids = [i[0] for i in get_id_by_class(self.db, cls)]
                self.send_many_users(send_ids, text)
            except:
                self.send_console('Лол дебил\nРассылка класс <класс>_<текст>')
        elif 'рассылка параллель' in msg:
            try:
                par, text = event.obj.text.split('_')
                par = par[19:].upper()
                send_ids = [i[0] for i in get_by_parallel(self.db, par)]
                self.send_many_users(send_ids, text)
            except:
                self.send_console('Лол дебил\nРассылка параллель <параллель>_<текст>')
        elif 'ответ' in msg[:7]:
            if 'reply_message' in event.obj.keys():
                try:
                    reply_text = event.obj.text[6:]
                    reply = event.obj.reply_message['text']
                    reply_id = reply[reply.find('[') + 1:reply.find('|')][2:]
                    self.send_msg(reply_id, reply_text)
                    self.send_console('Ответ отправлен!')
                except:
                    self.send_console('Хороший тамада и конкурсы интересные')
            else:
                self.send_console('Сообщение мне перешли')
        elif 'удалить' in msg:
            uid = int(msg.lstrip('удалить '))
            if get_by_id(self.db, uid):
                name, last, cls, requests = get_by_id(self.db, uid)[0]
                del_by_id(self.db, uid)
                self.send_console(f'Пользователь @id{uid}({name} {last}) ({cls}) удален!')
                decrease_users(self.db)
            else:
                self.send_console('Пользователь не найден в базе!')
        elif 'инфо' in msg:
            if 'имя' in msg:
                name, last = [i.title().strip() for i in msg[9:].split(' ')]
                try:
                    name, last, cls, uid, requests, gratitudes = get_by_name(self.db, name, last)[0]
                    self.send_console(f'Пользователь @id{uid}({name} {last}) ({cls})\n'
                                      f'id: {uid}\n'
                                      f'Запросов: {requests}\n'
                                      f'Благодарностей: {gratitudes}\n'
                                      f'Уведомления: {"включены" if get_notifications(self.db, uid) else "выключены"}')
                except:
                    self.send_console('Пользователь не найден в базе!')
            else:
                uid = int(msg.lstrip('инфо '))
                if get_by_id(self.db, uid):
                    name, last, cls, requests = get_by_id(self.db, uid)[0]
                    self.send_console(f'Пользователь @id{uid}({name} {last}) ({cls})\n'
                                      f'id: {uid}\n'
                                      f'Запросов: {requests}')
                else:
                    self.send_console('Пользователь не найден в базе!')
        elif 'рассылка расписания' in msg:
            if pendulum.today(tz='Europe/Moscow').weekday() == 5:
                sf_date = saturday()
            else:
                sf_date = pendulum.tomorrow(tz='Europe/Moscow').__format__('DD.MM.YYYY')

            self.load_schedule_date(sf_date)
            text = ''
            if msg != 'рассылка расписания':
                text = event.obj.text[20:]
            for i in cst.classes:
                send_ids = [i[0] for i in get_id_by_class(self.db, i)]
                if send_ids:
                    try:
                        self.send_schedule(send_ids, self.schedules[i], text)
                        self.send_console(f'Отправлено расписание пользователям {i} класса!')
                    except:
                        self.send_console(f'Ошибка на {i} классе!\nКто-то не получил расписание...')
                else:
                    self.send_console(f'Нет юзеров из {i} класса!')
        elif 'sql' in msg:
            req = event.obj.text[4:]
            cur = self.db.cursor()
            res = cur.execute(
                f"""
                {req}
                """
            ).fetchall()
            self.send_console(f'{res}')
        elif 'ошибка_расписания' in msg:
            update_time = msg.lstrip('ошибка_расписания ')
            s = {}
            upload = vk_api.VkUpload(self.vk)
            for i in cst.classes:
                copy('labels/error.png', f'{update_time}/{i}.png')
                s.update({i: upload_class(i, upload, update_time)})

            with open(f'uploaded_photo/{update_time}.sf', 'wb') as f:
                dump(s, f)
            self.send_console(f'Все классы на {update_time} заменены ошибкой!')
        elif 'замена_общим' in msg:
            update_time = msg.lstrip('замена_общим ')
            s = {}
            upload = vk_api.VkUpload(self.vk)
            main = upload_pic(f'source/{update_time}.png', upload)
            for i in cst.classes:
                print(i, end=' ')
                s.update({i: main})

            with open(f'uploaded_photo/{update_time}.sf', 'wb') as f:
                dump(s, f)
            self.send_console(f'Все классы на {update_time} заменены общим расписанием!')

    def send_console(self, message):
        self.vk_api.messages.send(peer_id=cst.console_id,
                                  message=message,
                                  random_id=get_random_id())

    def load_schedule(self):
        with open(f'uploaded_photo/{get_schedule_date()}.sf', 'rb') as f:
            self.schedules = load(f)

    def load_schedule_date(self, s_date):
        with open(f'uploaded_photo/{s_date}.sf', 'rb') as f:
            self.schedules = load(f)

    def send_attachment(self, send_id, msg, attachment):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=msg,
                                  random_id=get_random_id(),
                                  attachment=attachment)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())

    def send_photo_console(self, root='img.png', msg=''):
        self.upload = VkUpload(self.vk)
        response = self.upload.photo_messages(root)[0]
        attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
        self.vk_api.messages.send(peer_id=cst.console_id,
                                  message=msg,
                                  random_id=get_random_id(),
                                  attachment=attachment)

    def get_stat(self):
        cur = self.db.cursor()
        res = cur.execute(
            f"""
            SELECT * from stat WHERE date = '{now(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
            """
        ).fetchall()
        if res:
            self.send_console(f'Краткая статистика:\n'
                              f'Юзеров: {res[0][2]}\n'
                              f'Запросов: {res[0][1]}\n'
                              f'Благодарностей: {res[0][3]}')
        else:
            yesterday_res = cur.execute(
                f"""
                SELECT * from stat WHERE date = '{yesterday(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
                """
            ).fetchall()[0]
            res = cur.execute(
                f"""
                INSERT INTO stat (date, users, requests, gratitudes)
                
                VALUES (?, ?, ?, ?)
                """,
                (now(tz="Europe/Moscow").__format__("YYYY-MM-DD"), yesterday_res[1], yesterday_res[2],
                 yesterday_res[3])).fetchall()
            self.db.commit()
            self.get_stat()

    def full_stat(self):
        self.get_stat()
        cls_us = {'5А': 0, '5Б': 0, '5В': 0, '5Г': 0, '6А': 0, '6Б': 0, '6В': 0, '7А': 0,
                  '7Б': 0, '7В': 0, '8А': 0, '8Б': 0, '8В': 0, '9А': 0, '9Б': 0, '9В': 0,
                  '10А': 0, '10Б': 0, '10В': 0, '10Г': 0, '11А': 0, '11Б': 0, '11В': 0,
                  '11Г': 0, 'NS': 0}
        p_us = {'5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0, '11': 0}

        for i in range(5, 12):
            cur = self.db.cursor()
            res = cur.execute(
                f"""
                SELECT * FROM users
                WHERE cls_num = {i}
                """).fetchall()
            p_us[str(i)] = len(res)

        for i in cst.classes:
            cur = self.db.cursor()
            res = cur.execute(
                f"""
                SELECT * FROM users
                WHERE cls = '{i}'
                """).fetchall()
            cls_us[i] = len(res)

        c = 0
        stat_out = 'Статистика по классам:\n'
        u_count = sum(p_us.values())
        print(u_count)
        for i in cst.classes:
            c += 1
            stat_out += f'{str(i).ljust(4)} - {cls_us[i]} ({"%.2f" % (cls_us[i] * 100 / u_count)}%)\t\t'
            if c % 2 == 0:
                stat_out += '\n'

        stat_out += '\n\nСтатистика по параллелям:\n'
        c = 0
        for i in range(5, 12):
            c += 1
            stat_out += f'{i} - {p_us[str(i)]} ({"%.2f" % (p_us[str(i)] * 100 / u_count)}%)\t\t'
            if c % 2 == 0:
                stat_out += '\n'

        self.send_console(stat_out)

        plt.rcParams.update({'font.size': 6})
        fig1, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(6, 6))
        labels = cls_us.keys()
        values = cls_us.values()
        ax1.bar(labels, values)
        ax1.set_title(f'Статистика пользователей {now(tz="Europe/Moscow").__format__("YYYY-MM-DD")}')

        labels = p_us.keys()
        values = p_us.values()
        ax2.bar(labels, values)
        plt.savefig(f'statistic/stat{date(today().year, today().month, today().day).__format__("DD.MM.YYYY")}.png')
        self.send_photo_console(
            f'statistic/stat{date(today().year, today().month, today().day).__format__("DD.MM.YYYY")}.png',
            'Статистика')

    def send_schedule(self, users, schedule, text=''):
        self.vk_api.messages.send(user_ids=users,
                                  attachment=schedule,
                                  message=f'Держи расписание на завтра! '
                                          f'{cst.smiles_answer[randint(0, len(cst.smiles_answer) - 1)]}\n{text}',
                                  random_id=get_random_id())

    def send_many_users(self, users, text):
        self.vk_api.messages.send(user_ids=users,
                                  message=text,
                                  random_id=get_random_id())
