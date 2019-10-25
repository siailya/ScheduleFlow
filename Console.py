from vk_api.utils import get_random_id

from Constantes import Constantes as cst
from Keyboards import Keyboards
from Process import download_all
from Utilities import get_schedule_date


class Console:
    def __init__(self, vk_api, event, base, stat):
        self.base = base
        self.vk_api = vk_api
        self.stat = stat
        self.console(event)

    def console(self, event):
        Keyboards(self.vk_api).conslole_keyboard()
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
            download_all()
            self.send_console(f'Расписание на {get_schedule_date()} обновлено!')
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
        elif 'общая рассылка лс' in msg:
            ms = event.obj.text[18:]
            count = 0
            er = 0
            for i in self.base.keys():
                try:
                    self.send_msg(i, ms)
                    count += 1
                except:
                    er += 1
            self.send_console(f'Отправлено: {count}\nОшибок; {er}')
        elif 'сообщение юзеру' in msg:
            idu, ms = event.obj.text[16:].split('_')
            self.send_msg(idu, ms)
        elif 'рассылка класс' in msg:
            cls, text = event.obj.text[15:].split('_')
            count = 0
            er = 0
            for i in self.base.keys():
                if self.base[i][2] == cls.lower():
                    try:
                        self.send_msg(i, text)
                        count += 1
                    except:
                        er += 1
                self.send_console(f'Отправлено: {count}\nОшибок: {er}')
        elif 'рассылка параллель' in msg:
            pr, ms = event.obj.text[19:].split('_')
            count = 0
            er = 0
            for i in self.base.keys():
                if pr in self.base[i][2]:
                    try:
                        self.send_msg(i, ms)
                        count += 1
                    except:
                        er += 1
            self.send_console(f'Отправлено: {count}\nОшибок: {er}')
        elif 'ответ' in msg:
            print(event.obj)

    def send_console(self, message):
        self.vk_api.messages.send(peer_id=cst.console_id,
                                  message=message,
                                  random_id=get_random_id())

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())