from os import path, remove
from pickle import load
from random import randint

from vk_api import VkUpload
from vk_api.utils import get_random_id
from pendulum import today, date
from Constantes import Constantes as cst
from Process import download_all
import matplotlib.pyplot as plt
from Utilities import get_schedule_date, get_picture
from Base import write_base


class Console:
    def __init__(self, vk_api, event, base, stat, vk):
        self.vk_api = vk_api
        self.vk = vk
        self.base = base
        self.stat = stat
        self.schedules = {}
        if event.obj.text:
            self.console(event)
        else:
            if randint(0, 100) >= 90:
                self.send_console('Очень интересно')

    def console(self, event):
        # Keyboards(self.vk_api).conslole_keyboard()
        msg = event.obj.text.lower().replace('@', '')
        if msg == '[club187161295|scheduleflow] пользователи':
            u = 'Список юзеров:\n'
            c = 0
            for i in self.base.keys():
                c += 1
                u += f'@id{i}({self.base[i][0]} {self.base[i][1]}) - ' \
                     f'{self.base[i][2].upper()}\n'
                if c >= 50:
                    c = 0
                    self.send_console(u)
                    u = ''
            self.send_console(u)
        elif msg == '[club187161295|scheduleflow] обновить':
            if path.exists(f'source/{get_schedule_date()}.png'):
                remove(f'source/{get_schedule_date()}.png')
                if path.exists(f'uploaded_photo/{get_schedule_date()}.sf'):
                    remove(f'uploaded_photo/{get_schedule_date()}.sf')
                get_picture()
                download_all()
                self.send_console(f'Расписание на {get_schedule_date()} обновлено!')
            else:
                self.send_console(f'Кажется, обновлять нечего!')
                download_all()
                self.send_console(f'Расписание на {get_schedule_date()} загружено!')
        elif msg == '[club187161295|scheduleflow] статистика':
            self.send_console(f'Число запросов расписания: '
                              f'{self.stat["requests"]}\nЧисло юзеров: '
                              f'{self.stat["users"]}\n'
                              f'Благодарностей: {self.stat["thank"]}')
        elif msg == '[club187161295|scheduleflow] полная статистика':
            cls_us = {'5А': 0, '5Б': 0, '5В': 0, '5Г': 0, '6А': 0, '6Б': 0, '6В': 0, '7А': 0,
                      '7Б': 0, '7В': 0, '8А': 0, '8Б': 0, '8В': 0, '9А': 0, '9Б': 0, '9В': 0,
                      '10А': 0, '10Б': 0, '10В': 0, '10Г': 0, '11А': 0, '11Б': 0, '11В': 0,
                      '11Г': 0, 'NS': 0}
            p_us = {'5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0, '11': 0}

            c_state = 'Статистика по классам:\n'
            for i in self.base.keys():
                cls_us[self.base[i][2].upper()] = cls_us.get(self.base[i][2].upper(), 0) + 1
            for i in cls_us.keys():
                c_state += f'{i.upper()}: {cls_us[i.upper()]} (' \
                           f'{"%.2f" % (cls_us[i.upper()] / self.stat["users"] * 100)}%)\n'

            p_state = 'Статистика по параллелям\n'
            for i in self.base.keys():
                if len(self.base[i][2]) == 2:
                    p = self.base[i][2][0]
                else:
                    p = self.base[i][2][:2]
                p_us[p] = p_us.get(p, 0) + 1
            for i in p_us.keys():
                p_state += f'{i} классы: {p_us[i]} (' \
                           f'{"%.2f" % (p_us[i] / self.stat["users"] * 100)}%)\n'

            self.send_console(f'Число запросов расписания: '
                              f'{self.stat["requests"]}\nЧисло юзеров: '
                              f'{self.stat["users"]}\n'
                              f'Благодарностей: {self.stat["thank"]}\n\n'
                              f'{c_state}\n\n{p_state}')

            plt.rcParams.update({'font.size': 5})
            fig1, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(4, 4))
            labels = cls_us.keys()
            values = cls_us.values()
            ax1.bar(labels, values)

            labels = p_us.keys()
            values = p_us.values()
            ax2.bar(labels, values)
            plt.savefig(f'statistic/stat'
                        f'{date(today().year, today().month, today().day).__format__("DD.MM.YYYY")}.png')
            self.send_photo_console(f'statistic/'
                                    f'stat{date(today().year, today().month, today().day).__format__("DD.MM.YYYY")}.png', 'Статистика')

        elif 'общая рассылка лс' in msg:
            ms = event.obj.text[18:]
            count = 0
            er = []
            for i in self.base.keys():
                try:
                    self.send_msg(i, ms)
                    count += 1
                except:
                    er.append(i)
            self.send_console(f'Отправлено: {count}\nОшибок: {" ".join(er)}')
        elif 'сообщение юзеру' in msg:
            idu, ms = event.obj.text[16:].split('_')
            self.send_msg(idu, ms)
        elif 'рассылка класс' in msg:
            cls, text = event.obj.text[15:].split('_')
            count = 0
            er = []
            for i in self.base.keys():
                if self.base[i][2] == cls.lower():
                    try:
                        self.send_msg(i, text)
                        count += 1
                    except:
                        er.append(i)
                self.send_console(f'Отправлено: {count}\nОшибок: {" ".join(er)}')
        elif 'рассылка параллель' in msg:
            pr, ms = event.obj.text[19:].split('_')
            count = 0
            er = []
            for i in self.base.keys():
                if pr in self.base[i][2]:
                    try:
                        self.send_msg(i, ms)
                        count += 1
                    except:
                        er.append(i)
            self.send_console(f'Отправлено: {count}\nОшибки: {" ".join(er)}')
        elif 'ответ' in msg:
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
            uid = msg.lstrip('удалить ')
            p = self.base.pop(int(uid), 0)
            if p:
                self.send_console(f'Пользователь @id{uid} удален')
            else:
                self.send_console('Не удален...')
            write_base(self.base, self.stat)
            print(self.base)
        elif 'рассылка расписания' in msg:
            self.load_schedule()
            k = 0
            e = []
            for i in self.base.keys():
                if self.base[i][4] == 1:
                    try:
                        self.send_attachment(i, f'Держи расписание на завтра! ;-)',
                                             self.schedules[self.base[i][2].upper()])
                        k += 1
                    except:
                        e.append(i)
            self.send_console(f'Отправлено: {k}\nОшибки: {" ".join(e)}')

    def send_console(self, message):
        self.vk_api.messages.send(peer_id=cst.console_id,
                                  message=message,
                                  random_id=get_random_id())

    def load_schedule(self):
        with open(f'uploaded_photo/{get_schedule_date()}.sf', 'rb') as f:
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